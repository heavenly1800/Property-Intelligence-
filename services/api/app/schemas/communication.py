from typing import Literal
from pydantic import BaseModel,Field
Channel=Literal["email","sms"]
class TemplateInput(BaseModel):
 template_name:str=Field(min_length=1);channel:Channel;category:str;subject_template:str|None=None;body_template:str=Field(min_length=1);variables:list[str]=[];active:bool=True;version:int=1
class TemplatePatch(BaseModel):
 template_name:str|None=None;category:str|None=None;subject_template:str|None=None;body_template:str|None=None;variables:list[str]|None=None;active:bool|None=None;version:int|None=None
class PreviewRequest(BaseModel):variables:dict[str,str|float|int|None]={}
class DraftRequest(BaseModel):
 contact_id:str;channel:Channel;template_id:str|None=None;subject:str|None=None;body:str|None=None;variables:dict[str,str|float|int|None]={};scheduled_for:str|None=None;related_offer_id:str|None=None;related_task_id:str|None=None;create_follow_up:bool=False;follow_up_title:str|None=None;follow_up_due_at:str|None=None
class MessagePatch(BaseModel):subject:str|None=None;body:str|None=None;scheduled_for:str|None=None;status:str|None=None;related_offer_id:str|None=None;related_task_id:str|None=None
class SendRequest(BaseModel):confirm_send:bool=False
