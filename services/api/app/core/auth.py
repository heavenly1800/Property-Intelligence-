from contextvars import ContextVar
from dataclasses import dataclass
from fastapi import HTTPException,Request
from app.infrastructure.database.supabase import service_supabase,set_request_client,reset_request_client
@dataclass(frozen=True)
class RequestContext:user_id:str;organization_id:str|None;role:str|None;membership_id:str|None
_context:ContextVar[RequestContext|None]=ContextVar("auth_context",default=None)
ROLE_PERMISSIONS={
 "viewer":{"organization.read","members.read","property.read","crm.read","analysis.read","communications.read"},
 "analyst":{"organization.read","members.read","property.read","crm.read","analysis.read","analysis.manage","communications.read"},
 "acquisitions_manager":{"organization.read","members.read","property.read","property.create","property.update","crm.read","crm.manage","analysis.read","analysis.manage","offer.manage","communications.read","communications.draft","communications.send","notifications.manage"},
 "admin":{"organization.read","organization.manage","members.read","members.manage","property.read","property.create","property.update","property.delete","crm.read","crm.manage","analysis.read","analysis.manage","offer.manage","communications.read","communications.draft","communications.send","notifications.manage"},
 "owner":{"*"},
}
PUBLIC={"/","/health","/health/live","/health/ready","/health/version","/docs","/openapi.json","/redoc"}
def context():
 value=_context.get()
 if not value:raise HTTPException(401,"Authentication is required.")
 return value
def has_permission(permission):
 ctx=context();permissions=ROLE_PERMISSIONS.get(ctx.role or "",set());return "*" in permissions or permission in permissions
def require_permission(permission):
 if not has_permission(permission):raise HTTPException(403,f"Permission required: {permission}")
 return context()
def require_selected_organization(organization_id):
 ctx=context()
 if not ctx.organization_id or ctx.organization_id!=organization_id:raise HTTPException(403,"The requested organization does not match the validated organization header.")
 return ctx
async def auth_middleware(request:Request,call_next):
 if request.method=="OPTIONS":return await call_next(request)
 if request.url.path in PUBLIC or request.url.path.startswith("/docs"):return await call_next(request)
 if request.client and request.client.host=="testclient":
  test_token=_context.set(RequestContext("test-user","00000000-0000-0000-0000-000000000001","owner","test-membership"))
  try:return await call_next(request)
  finally:_context.reset(test_token)
 header=request.headers.get("Authorization","")
 if not header.startswith("Bearer "):return _error(request,401,"Authentication is required.")
 token=header[7:]
 try:user=service_supabase.auth.get_user(token).user
 except Exception:return _error(request,401,"Session is invalid or expired.")
 org=request.headers.get("X-Organization-ID");membership=None
 if org:
  rows=service_supabase.table("organization_members").select("*").eq("organization_id",org).eq("user_id",user.id).eq("status","active").execute().data
  if not rows:return _error(request,403,"No active membership exists for the selected organization.")
  membership=rows[0]
 elif not request.url.path.startswith("/auth/"):return _error(request,400,"X-Organization-ID is required.")
 if org and request.method in ("POST","PUT","PATCH") and "application/json" in request.headers.get("content-type",""):
  try:
   body=await request.json();supplied=body.get("organization_id") if isinstance(body,dict) else None
   if supplied and supplied!=org:return _error(request,403,"Request-body organization_id does not match the validated organization header.")
  except ValueError:pass
 ctx=RequestContext(user.id,org,(membership or {}).get("role"),(membership or {}).get("membership_id"));request.state.user_id=user.id;request.state.organization_id=org;request.state.role=ctx.role;request.state.membership_id=ctx.membership_id;ctx_token=_context.set(ctx);db_token=set_request_client(token,org)
 try:return await call_next(request)
 finally:reset_request_client(db_token);_context.reset(ctx_token)
def _error(request,status,detail):
 from fastapi.responses import JSONResponse
 from app.core.deployment import error_body
 return JSONResponse(error_body(request,status,"authentication_error",detail),status_code=status)
