import asyncio
import io
import json
import logging
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from fastapi import HTTPException
from fastapi.testclient import TestClient
from starlette.requests import Request
from starlette.responses import Response
from app.core.deployment import deployment_middleware
from app.core.resilience import InMemoryIdempotencyStore, InMemoryRateLimiter
from app.core.settings import Settings
from app.jobs import notification_scan

DUMMY={
 "SUPABASE_URL":"https://project.supabase.co",
 "SUPABASE_ANON_KEY":"anon-value",
 "SUPABASE_SERVICE_ROLE_KEY":"service-value",
 "OPENAI_API_KEY":"openai-value",
}

def settings(**values):
 return Settings(_env_file=None,**{**DUMMY,**values})

class DeploymentHardeningTest(unittest.TestCase):
 def test_environment_validation_and_production_placeholder_rejection(self):
  self.assertEqual(settings(APP_ENV="development").validation_errors(),[])
  errors=settings(APP_ENV="production",FRONTEND_ORIGINS="https://example.com",SUPABASE_SERVICE_ROLE_KEY="changeme").validation_errors()
  self.assertTrue(any("placeholder" in value for value in errors))

 def test_cors_and_docs_defaults(self):
  self.assertEqual(len(settings(APP_ENV="development").frontend_origins),2)
  self.assertTrue(settings(APP_ENV="development").docs_enabled)
  self.assertFalse(settings(APP_ENV="production",FRONTEND_ORIGINS="https://app.company.test").docs_enabled)
  self.assertIn("FRONTEND_ORIGINS is required.",settings(APP_ENV="staging",FRONTEND_ORIGINS="").validation_errors())

 def test_request_id_and_security_headers(self):
  request=Request({"type":"http","method":"GET","path":"/health/live","raw_path":b"/health/live","query_string":b"","headers":[(b"x-request-id",b"safe-123")],"client":("127.0.0.1",1),"server":("test",80),"scheme":"http"})
  async def downstream(_):return Response("ok",status_code=200)
  response=asyncio.run(deployment_middleware(request,downstream))
  self.assertEqual(response.headers["X-Request-ID"],"safe-123")
  self.assertEqual(response.headers["X-Content-Type-Options"],"nosniff")

 def test_rate_limit_and_retry_after(self):
  limiter=InMemoryRateLimiter();limiter.check("key",1,60)
  with self.assertRaises(HTTPException) as caught:limiter.check("key",1,60)
  self.assertEqual(caught.exception.status_code,429)
  self.assertIn("Retry-After",caught.exception.headers)

 def test_idempotent_replay_and_conflict(self):
  store=InMemoryIdempotencyStore();calls=[]
  with patch("app.core.resilience.get_settings",return_value=settings(IDEMPOTENCY_RETENTION_SECONDS=60)):
   first=store.run("scope","key",{"a":1},lambda:calls.append(1) or {"ok":True})
   replay=store.run("scope","key",{"a":1},lambda:calls.append(2))
   self.assertEqual(first,replay);self.assertEqual(calls,[1])
   with self.assertRaises(HTTPException) as caught:store.run("scope","key",{"a":2},lambda:None)
  self.assertEqual(caught.exception.status_code,409)

 def test_scanner_one_shot_exit_behavior_and_secret_free_log(self):
  output=io.StringIO()
  with patch.object(notification_scan,"acquire_lock",return_value=SimpleNamespace(close=lambda:None)),patch.object(notification_scan,"run_once",return_value={}),patch("sys.stdout",output):
   self.assertEqual(notification_scan.main(["--batch-size","1"]),0)
  self.assertIn("scanner_stopped",output.getvalue())
  self.assertNotIn(DUMMY["SUPABASE_SERVICE_ROLE_KEY"],output.getvalue())

 def test_scanner_distributed_lock_success_and_conflict(self):
  class Query:
   def delete(self):return self
   def eq(self,*_):return self
   def lt(self,*_):return self
   def insert(self,*_):return self
   def execute(self):return SimpleNamespace(data=[])
  database=SimpleNamespace(table=lambda _:Query())
  with patch("app.infrastructure.database.supabase.service_supabase",database):
   self.assertIsNotNone(notification_scan.acquire_distributed_lock(300))
  conflict=SimpleNamespace(table=lambda _:(_ for _ in ()).throw(RuntimeError("unique conflict")))
  with patch("app.infrastructure.database.supabase.service_supabase",conflict):
   self.assertIsNone(notification_scan.acquire_distributed_lock(300))

 def test_health_docs_errors_and_headers(self):
  from app.main import app
  client=TestClient(app)
  self.assertEqual(client.get("/health/live").status_code,200)
  self.assertEqual(client.get("/health/version").status_code,200)
  self.assertEqual(client.get("/docs").status_code,200)
  response=client.get("/not-a-route",headers={"X-Request-ID":"support-1"})
  self.assertEqual(response.status_code,404)
  self.assertEqual(response.json()["request_id"],"support-1")
  self.assertEqual(response.headers["X-Content-Type-Options"],"nosniff")

 def test_readiness_success_and_connectivity_failure(self):
  from app.main import app
  client=TestClient(app)
  query=SimpleNamespace(select=lambda *a,**k:query,limit=lambda *a,**k:query,execute=lambda:SimpleNamespace(data=[]))
  healthy=SimpleNamespace(table=lambda _:query)
  failing=SimpleNamespace(table=lambda _:(_ for _ in ()).throw(RuntimeError("database secret detail")))
  with patch("app.main.service_supabase",healthy):
   self.assertEqual(client.get("/health/ready").status_code,200)
  with patch("app.main.service_supabase",failing):
   response=client.get("/health/ready")
  self.assertEqual(response.status_code,503)
  self.assertNotIn("database secret detail",response.text)
