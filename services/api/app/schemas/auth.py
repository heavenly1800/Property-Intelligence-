from typing import Literal
from pydantic import BaseModel,Field
Role=Literal["owner","admin","acquisitions_manager","analyst","viewer"];Status=Literal["invited","active","suspended","removed"]
class BootstrapOrganization(BaseModel):name:str=Field(min_length=1);slug:str=Field(pattern=r"^[a-z0-9-]+$")
class OrganizationPatch(BaseModel):name:str|None=None;slug:str|None=None
class InviteMember(BaseModel):email:str;role:Role= "viewer";expires_hours:int=Field(default=72,ge=1,le=720)
class MemberPatch(BaseModel):role:Role|None=None;status:Status|None=None
class AcceptInvitation(BaseModel):token:str=Field(min_length=20)
