import asyncio,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from fastapi import HTTPException
from starlette.requests import Request
from starlette.responses import Response
from fastapi.testclient import TestClient
from app.main import app
from app.routers.auth import router as auth_router
from app.core import auth
from app.core.auth import RequestContext,has_permission,require_permission
from app.services.organization_service import OrganizationService

class Query:
 def __init__(self,data):self.data=data
 def select(self,*a,**k):return self
 def eq(self,*a):return self
 def ilike(self,*a):return self
 def in_(self,*a):return self
 def is_(self,*a):return self
 def insert(self,value):self.data=[value];return self
 def update(self,value):
  if not self.data:self.data=[value]
  else:self.data=[{**row,**value} for row in self.data]
  return self
 def upsert(self,value,**k):self.data=[value];return self
 def execute(self):return SimpleNamespace(data=self.data)
class FakeSupabase:
 def __init__(self,data,user="u1"):self.data=data;self.auth=SimpleNamespace(get_user=lambda token:SimpleNamespace(user=SimpleNamespace(id=user)))
 def table(self,name):return Query(self.data.get(name,[]))
class AuthTest(unittest.TestCase):
 def with_context(self,role,fn):
  token=auth._context.set(RequestContext("u","o",role,"m"))
  try:return fn()
  finally:auth._context.reset(token)
 def test_role_permission_boundaries(self):
  self.assertTrue(self.with_context("viewer",lambda:has_permission("property.read")));self.assertFalse(self.with_context("viewer",lambda:has_permission("property.update")));self.assertTrue(self.with_context("analyst",lambda:has_permission("analysis.manage")));self.assertFalse(self.with_context("analyst",lambda:has_permission("crm.manage")));self.assertTrue(self.with_context("acquisitions_manager",lambda:has_permission("offer.manage")));self.assertTrue(self.with_context("admin",lambda:has_permission("members.manage")))
 def test_unauthenticated_request_is_401(self):
  request=Request({"type":"http","method":"GET","path":"/properties/","raw_path":b"/properties/","query_string":b"","headers":[],"client":("127.0.0.1",1),"server":("test",80),"scheme":"http"});response=asyncio.run(auth.auth_middleware(request,lambda r:None));self.assertEqual(response.status_code,401)
 def test_options_preflight_bypasses_auth_and_includes_cors_headers(self):
  request=Request({"type":"http","method":"OPTIONS","path":"/auth/bootstrap-organization","raw_path":b"/auth/bootstrap-organization","query_string":b"","headers":[],"client":("127.0.0.1",1),"server":("test",80),"scheme":"http"})
  async def downstream(_):return Response(status_code=204)
  self.assertEqual(asyncio.run(auth.auth_middleware(request,downstream)).status_code,204)
  response=TestClient(app).options("/auth/bootstrap-organization",headers={"Origin":"http://localhost:5173","Access-Control-Request-Method":"POST","Access-Control-Request-Headers":"authorization,content-type"})
  self.assertEqual(response.status_code,200);self.assertEqual(response.headers.get("access-control-allow-origin"),"http://localhost:5173");self.assertIn("authorization",response.headers.get("access-control-allow-headers","").lower())
 def test_bootstrap_route_is_registered_at_reported_path(self):
  routes={(route.path,method) for route in auth_router.routes for method in getattr(route,"methods",set())}
  self.assertIn(("/auth/bootstrap-organization","POST"),routes);self.assertNotIn(("/auth/organizations","POST"),routes)
 def test_inactive_membership_and_cross_org_are_403(self):
  request=Request({"type":"http","method":"GET","path":"/properties/","raw_path":b"/properties/","query_string":b"","headers":[(b"authorization",b"Bearer valid"),(b"x-organization-id",b"other-org")],"client":("127.0.0.1",1),"server":("test",80),"scheme":"http"})
  with patch.object(auth,"service_supabase",FakeSupabase({"organization_members":[]})):response=asyncio.run(auth.auth_middleware(request,lambda r:None))
  self.assertEqual(response.status_code,403)
 def test_valid_authenticated_access_sets_trusted_context(self):
  request=Request({"type":"http","method":"GET","path":"/properties/","raw_path":b"/properties/","query_string":b"","headers":[(b"authorization",b"Bearer valid"),(b"x-organization-id",b"o")],"client":("127.0.0.1",1),"server":("test",80),"scheme":"http"})
  async def downstream(_):self.assertEqual(auth.context().organization_id,"o");self.assertEqual(auth.context().role,"viewer");return Response(status_code=204)
  fake=FakeSupabase({"organization_members":[{"membership_id":"m","role":"viewer"}]})
  with patch.object(auth,"service_supabase",fake),patch.object(auth,"set_request_client",return_value=object()),patch.object(auth,"reset_request_client"):response=asyncio.run(auth.auth_middleware(request,downstream))
  self.assertEqual(response.status_code,204)
 def test_request_body_organization_spoofing_is_rejected(self):
  body=b'{"organization_id":"other"}';sent=False
  async def receive():
   nonlocal sent
   if sent:return {"type":"http.disconnect"}
   sent=True;return {"type":"http.request","body":body,"more_body":False}
  request=Request({"type":"http","method":"POST","path":"/properties/","raw_path":b"/properties/","query_string":b"","headers":[(b"authorization",b"Bearer valid"),(b"x-organization-id",b"o"),(b"content-type",b"application/json")],"client":("127.0.0.1",1),"server":("test",80),"scheme":"http"},receive)
  fake=FakeSupabase({"organization_members":[{"membership_id":"m","role":"owner"}]})
  with patch.object(auth,"service_supabase",fake):response=asyncio.run(auth.auth_middleware(request,lambda _:None))
  self.assertEqual(response.status_code,403)
 def test_owner_only_promotion(self):
  with patch.object(OrganizationService,"member",return_value={"role":"viewer"}),patch("app.services.organization_service.service_supabase",FakeSupabase({})):
   with self.assertRaises(HTTPException) as caught:self.with_context("admin",lambda:OrganizationService.update_member("o","m",{"role":"owner"}))
  self.assertEqual(caught.exception.status_code,403)
 def test_final_owner_protection(self):
  with patch.object(OrganizationService,"member",return_value={"role":"owner"}),patch.object(OrganizationService,"owner_count",return_value=1):
   with self.assertRaises(HTTPException) as caught:self.with_context("owner",lambda:OrganizationService.update_member("o","m",{"status":"removed"}))
  self.assertEqual(caught.exception.status_code,409)
 def test_duplicate_invitation_prevention(self):
  fake=FakeSupabase({"organization_members":[{"membership_id":"existing"}]})
  with patch("app.services.organization_service.service_supabase",fake):
   with self.assertRaises(HTTPException) as caught:self.with_context("owner",lambda:OrganizationService.invite("o","a@example.com","viewer",72))
  self.assertEqual(caught.exception.status_code,409)
 def test_bootstrap_rejects_existing_membership(self):
  with patch("app.services.organization_service.service_supabase",FakeSupabase({"organization_members":[{"membership_id":"m"}]})):
   with self.assertRaises(HTTPException) as caught:self.with_context("owner",lambda:OrganizationService.bootstrap("Name","slug"))
  self.assertEqual(caught.exception.status_code,409)
 def test_first_organization_bootstrap_claims_development_data_org(self):
  dev={"organization_id":OrganizationService.DEVELOPMENT_ORGANIZATION_ID,"name":"Development","slug":"development"};fake=FakeSupabase({"organization_members":[],"organizations":[dev],"profiles":[],"organization_audit_events":[]})
  with patch("app.services.organization_service.service_supabase",fake):result=self.with_context(None,lambda:OrganizationService.bootstrap("My Team","my-team"))
  self.assertEqual(result["organization"]["organization_id"],OrganizationService.DEVELOPMENT_ORGANIZATION_ID);self.assertEqual(result["membership"]["role"],"owner")
 def test_expired_invitation_is_rejected(self):
  fake=FakeSupabase({"organization_invitations":[{"invitation_id":"i","membership_id":"m","organization_id":"o","expires_at":"2000-01-01T00:00:00+00:00"}]})
  with patch("app.services.organization_service.service_supabase",fake):
   with self.assertRaises(HTTPException) as caught:self.with_context(None,lambda:OrganizationService.accept_invitation("expired"))
  self.assertEqual(caught.exception.status_code,410)
 def test_migration_scopes_prop_001_and_enables_rls(self):
  sql=(Path(__file__).parents[3]/"database/migrations/021_add_auth_organizations_rls.sql").read_text()
  self.assertIn("00000000-0000-0000-0000-000000000001",sql);self.assertIn("enable row level security",sql);self.assertIn("active_org_member",sql);self.assertIn("update %I set organization_id",sql)
