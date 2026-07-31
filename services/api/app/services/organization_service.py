import hashlib,secrets
from datetime import datetime,timedelta,timezone
from fastapi import HTTPException
from app.core.auth import context,require_permission,require_selected_organization
from app.infrastructure.database.supabase import service_supabase
class OrganizationService:
 DEVELOPMENT_ORGANIZATION_ID="00000000-0000-0000-0000-000000000001"
 @staticmethod
 def memberships(user_id):return service_supabase.table("organization_members").select("*,organizations(*)").eq("user_id",user_id).eq("status","active").execute().data
 @classmethod
 def bootstrap(cls,name,slug):
  ctx=context();existing=service_supabase.table("organization_members").select("membership_id").eq("user_id",ctx.user_id).in_("status",["invited","active"]).execute().data
  if existing:raise HTTPException(409,"User already has an organization membership.")
  development_members=service_supabase.table("organization_members").select("membership_id").eq("organization_id",cls.DEVELOPMENT_ORGANIZATION_ID).eq("status","active").execute().data
  development_org=service_supabase.table("organizations").select("*").eq("organization_id",cls.DEVELOPMENT_ORGANIZATION_ID).execute().data
  if development_org and not development_members:
   org=service_supabase.table("organizations").update({"name":name,"slug":slug,"created_by":ctx.user_id}).eq("organization_id",cls.DEVELOPMENT_ORGANIZATION_ID).execute().data[0]
  else:org=service_supabase.table("organizations").insert({"name":name,"slug":slug,"created_by":ctx.user_id}).execute().data[0]
  member=service_supabase.table("organization_members").insert({"organization_id":org["organization_id"],"user_id":ctx.user_id,"role":"owner","status":"active","joined_at":datetime.now(timezone.utc).isoformat()}).execute().data[0];service_supabase.table("profiles").upsert({"user_id":ctx.user_id,"default_organization_id":org["organization_id"]},on_conflict="user_id").execute();cls.audit(org["organization_id"],ctx.user_id,"organization_bootstrapped","organization",org["organization_id"]);return {"organization":org,"membership":member}
 @classmethod
 def invite(cls,organization_id,email,role,expires_hours):
  ctx=require_selected_organization(organization_id);require_permission("members.manage");existing=service_supabase.table("organization_members").select("membership_id").eq("organization_id",organization_id).ilike("invited_email",email).in_("status",["invited","active"]).execute().data
  if existing:raise HTTPException(409,"An active or pending membership already exists for this email.")
  if role=="owner" and ctx.role!="owner":raise HTTPException(403,"Only an owner can promote or invite an owner.")
  member=service_supabase.table("organization_members").insert({"organization_id":organization_id,"role":role,"status":"invited","invited_email":email.lower(),"invited_by":ctx.user_id}).execute().data[0];raw=secrets.token_urlsafe(32);expires=datetime.now(timezone.utc)+timedelta(hours=expires_hours);service_supabase.table("organization_invitations").insert({"organization_id":organization_id,"membership_id":member["membership_id"],"token_hash":hashlib.sha256(raw.encode()).hexdigest(),"expires_at":expires.isoformat()}).execute();cls.audit(organization_id,ctx.user_id,"invitation_created","membership",member["membership_id"],{"email":email,"role":role});return {"membership":member,"invitation_token":raw,"invitation_link":f"/invitations/accept?token={raw}","expires_at":expires.isoformat()}
 @classmethod
 def accept_invitation(cls,raw_token):
  ctx=context();token_hash=hashlib.sha256(raw_token.encode()).hexdigest();rows=service_supabase.table("organization_invitations").select("*").eq("token_hash",token_hash).is_("accepted_at","null").execute().data
  if not rows:raise HTTPException(404,"Invitation is invalid or already used.")
  invitation=rows[0]
  if datetime.fromisoformat(invitation["expires_at"].replace("Z","+00:00"))<=datetime.now(timezone.utc):raise HTTPException(410,"Invitation has expired.")
  member=service_supabase.table("organization_members").update({"user_id":ctx.user_id,"status":"active","joined_at":datetime.now(timezone.utc).isoformat()}).eq("membership_id",invitation["membership_id"]).eq("status","invited").execute().data
  if not member:raise HTTPException(409,"Invitation membership is no longer pending.")
  now=datetime.now(timezone.utc).isoformat();service_supabase.table("organization_invitations").update({"accepted_at":now}).eq("invitation_id",invitation["invitation_id"]).execute();service_supabase.table("profiles").upsert({"user_id":ctx.user_id,"default_organization_id":invitation["organization_id"]},on_conflict="user_id").execute();cls.audit(invitation["organization_id"],ctx.user_id,"invitation_accepted","membership",invitation["membership_id"]);return member[0]
 @classmethod
 def update_member(cls,organization_id,membership_id,data):
  ctx=require_selected_organization(organization_id);require_permission("members.manage");target=cls.member(organization_id,membership_id)
  if data.get("role")=="owner" and ctx.role!="owner":raise HTTPException(403,"Only an owner can promote another owner.")
  removing_owner=target.get("role")=="owner" and (data.get("role") not in(None,"owner") or data.get("status") in("suspended","removed"))
  if removing_owner and cls.owner_count(organization_id)<=1:raise HTTPException(409,"The final active owner cannot be removed, suspended, or demoted.")
  row=service_supabase.table("organization_members").update({**data,"updated_at":datetime.now(timezone.utc).isoformat()}).eq("organization_id",organization_id).eq("membership_id",membership_id).execute().data[0];cls.audit(organization_id,ctx.user_id,"membership_updated","membership",membership_id,data);return row
 @classmethod
 def remove_member(cls,organization_id,membership_id):return cls.update_member(organization_id,membership_id,{"status":"removed"})
 @staticmethod
 def member(org,mid):
  rows=service_supabase.table("organization_members").select("*").eq("organization_id",org).eq("membership_id",mid).execute().data
  if not rows:raise HTTPException(404,"Membership was not found.")
  return rows[0]
 @staticmethod
 def owner_count(org):return len(service_supabase.table("organization_members").select("membership_id").eq("organization_id",org).eq("role","owner").eq("status","active").execute().data)
 @staticmethod
 def audit(org,user,event,entity_type,entity_id,metadata=None):service_supabase.table("organization_audit_events").insert({"organization_id":org,"actor_user_id":user,"event_type":event,"entity_type":entity_type,"entity_id":str(entity_id),"metadata":metadata or {}}).execute()
