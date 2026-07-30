import os
from contextvars import ContextVar
from dotenv import load_dotenv
from supabase import create_client
load_dotenv()
url=os.getenv("SUPABASE_URL");service_key=os.getenv("SUPABASE_SERVICE_ROLE_KEY");anon_key=os.getenv("SUPABASE_ANON_KEY")
if not url or not service_key or not anon_key:raise RuntimeError("SUPABASE_URL, SUPABASE_ANON_KEY, and SUPABASE_SERVICE_ROLE_KEY are required.")
service_supabase=create_client(url,service_key)
_request_client:ContextVar[object|None]=ContextVar("request_supabase",default=None)
class ScopedSupabase:
 def __getattr__(self,name):return getattr(_request_client.get() or service_supabase,name)
supabase=ScopedSupabase()
def set_request_client(access_token:str,organization_id:str|None):
 client=create_client(url,anon_key);client.postgrest.auth(access_token)
 if organization_id:client.postgrest.headers["X-Organization-ID"]=organization_id
 return _request_client.set(client)
def reset_request_client(token):_request_client.reset(token)
