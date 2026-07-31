from fastapi import APIRouter,HTTPException,Request
from app.core.auth import context,require_permission,require_selected_organization
from app.infrastructure.database.supabase import service_supabase
from app.schemas.auth import AcceptInvitation,BootstrapOrganization,InviteMember,MemberPatch,OrganizationPatch
from app.services.organization_service import OrganizationService
from app.core.resilience import protected_operation
router=APIRouter(tags=["Authentication & Organizations"])
@router.get("/auth/me")
async def me():
 ctx=context();profile=service_supabase.table("profiles").select("*").eq("user_id",ctx.user_id).execute().data;return {"user_id":ctx.user_id,"profile":profile[0] if profile else None,"selected_organization_id":ctx.organization_id,"role":ctx.role,"membership_id":ctx.membership_id}
@router.get("/auth/organizations")
async def organizations():return OrganizationService.memberships(context().user_id)
@router.post("/auth/bootstrap-organization")
async def bootstrap(data:BootstrapOrganization,request:Request):return protected_operation(request,"organization-bootstrap",data.model_dump(),lambda:OrganizationService.bootstrap(data.name,data.slug))
@router.post("/auth/invitations/accept")
async def accept_invitation(request:AcceptInvitation):return OrganizationService.accept_invitation(request.token)
@router.post("/auth/select-organization")
async def select_organization():
 ctx=context()
 if not ctx.organization_id:raise HTTPException(400,"X-Organization-ID is required.")
 return {"organization_id":ctx.organization_id,"validated":True}
@router.get("/organizations/{organization_id}")
async def get_organization(organization_id:str):
 require_selected_organization(organization_id);require_permission("organization.read");rows=service_supabase.table("organizations").select("*").eq("organization_id",organization_id).execute().data
 if not rows:raise HTTPException(404,"Organization was not found.")
 return rows[0]
@router.patch("/organizations/{organization_id}")
async def update_organization(organization_id:str,request:OrganizationPatch):
 ctx=require_selected_organization(organization_id);require_permission("organization.manage");rows=service_supabase.table("organizations").update(request.model_dump(exclude_unset=True)).eq("organization_id",organization_id).execute().data;OrganizationService.audit(organization_id,ctx.user_id,"organization_updated","organization",organization_id,request.model_dump(exclude_unset=True));return rows[0]
@router.get("/organizations/{organization_id}/members")
async def members(organization_id:str):require_selected_organization(organization_id);require_permission("members.read");return service_supabase.table("organization_members").select("*").eq("organization_id",organization_id).execute().data
@router.post("/organizations/{organization_id}/members/invite")
async def invite(organization_id:str,data:InviteMember,request:Request):return protected_operation(request,"member-invitation",{"organization_id":organization_id,**data.model_dump()},lambda:OrganizationService.invite(organization_id,data.email,data.role,data.expires_hours))
@router.patch("/organizations/{organization_id}/members/{membership_id}")
async def update_member(organization_id:str,membership_id:str,request:MemberPatch):return OrganizationService.update_member(organization_id,membership_id,request.model_dump(exclude_unset=True))
@router.delete("/organizations/{organization_id}/members/{membership_id}")
async def delete_member(organization_id:str,membership_id:str):return OrganizationService.remove_member(organization_id,membership_id)
