from typing import Literal
from pydantic import BaseModel, Field

WorkflowStage=Literal["NEW_LEAD","RESEARCH","READY_TO_OFFER","OFFER_SENT","NEGOTIATING","UNDER_CONTRACT","MARKETING","SOLD","ARCHIVED"]
DeadlineType=Literal["next_seller_follow_up","offer_expiration","inspection","due_diligence","earnest_money","closing","buyer_marketing","assignment","custom"]

class ContactInput(BaseModel):
 first_name:str|None=None; last_name:str|None=None; company_name:str|None=None; role:str|None=None; phone:str|None=None; email:str|None=None; mailing_address:str|None=None; preferred_contact_method:str|None=None; best_contact_time:str|None=None; is_primary:bool=False; contact_status:str="active"; notes:str|None=None
class ContactPatch(BaseModel):
 first_name:str|None=None; last_name:str|None=None; company_name:str|None=None; role:str|None=None; phone:str|None=None; email:str|None=None; mailing_address:str|None=None; preferred_contact_method:str|None=None; best_contact_time:str|None=None; is_primary:bool|None=None; contact_status:str|None=None; notes:str|None=None
class TaskInput(BaseModel):
 contact_id:str|None=None; title:str=Field(min_length=1); description:str|None=None; task_type:str="follow_up"; due_at:str|None=None; priority:str="normal"; status:str="open"; assigned_to:str|None=None; reminder_at:str|None=None
class TaskPatch(BaseModel):
 contact_id:str|None=None; title:str|None=None; description:str|None=None; task_type:str|None=None; due_at:str|None=None; priority:str|None=None; status:str|None=None; assigned_to:str|None=None; reminder_at:str|None=None
class NoteInput(BaseModel):
 contact_id:str|None=None; note_type:str="general"; body:str=Field(min_length=1); is_pinned:bool=False
class NotePatch(BaseModel):
 contact_id:str|None=None; note_type:str|None=None; body:str|None=None; is_pinned:bool|None=None
class StageChange(BaseModel):
 to_stage:WorkflowStage; reason:str|None=None; changed_by:str|None=None
class DeadlineInput(BaseModel):
 deadline_type:DeadlineType; title:str=Field(min_length=1); due_at:str; status:str="open"; notes:str|None=None
class DeadlinePatch(BaseModel):
 deadline_type:DeadlineType|None=None; title:str|None=None; due_at:str|None=None; status:str|None=None; notes:str|None=None
class SentOfferInput(BaseModel):
 offer_analysis_id:str|None=None; contact_id:str|None=None; offer_amount:float=Field(gt=0); sent_at:str|None=None; delivery_method:str|None=None; expiration_at:str|None=None; status:str="sent"; response_notes:str|None=None
class SentOfferPatch(BaseModel):
 contact_id:str|None=None; offer_amount:float|None=Field(default=None,gt=0); sent_at:str|None=None; delivery_method:str|None=None; expiration_at:str|None=None; status:str|None=None; response_notes:str|None=None
