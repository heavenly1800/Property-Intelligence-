from fastapi import APIRouter,HTTPException,Request
from app.infrastructure.database.communication_repository import CommunicationRepository
from app.infrastructure.database.crm_repository import CrmRepository
from app.schemas.communication import DraftRequest,MessagePatch,PreviewRequest,SendRequest,TemplateInput,TemplatePatch
from app.schemas.crm import ConsentPatch
from app.services.communication_service import CommunicationService
from app.core.settings import get_settings
from app.core.auth import require_permission
from app.core.resilience import protected_operation
router=APIRouter(tags=["Seller Communications"])
@router.get("/communications/configuration")
async def communication_configuration():
 s=get_settings();return {"communications_enabled":s.COMMUNICATIONS_ENABLED,"email_provider":s.EMAIL_PROVIDER,"sms_provider":s.SMS_PROVIDER,"allow_console_delivery":s.ALLOW_CONSOLE_DELIVERY,"send_available":s.COMMUNICATIONS_ENABLED and s.ALLOW_CONSOLE_DELIVERY,"blocked_reason":None if s.COMMUNICATIONS_ENABLED and s.ALLOW_CONSOLE_DELIVERY else "External communications are disabled or no delivery provider is configured."}
def required(value,message="Record was not found."):
 if not value:raise HTTPException(404,message)
 return value
def safe(call):
 try:return call()
 except ValueError as exc:raise HTTPException(422,str(exc)) from exc

@router.get("/communication-templates")
async def templates():return CommunicationRepository.templates()
@router.post("/communication-templates")
async def create_template(request:TemplateInput):
 safe(lambda:CommunicationService.render(request.subject_template,request.body_template,{x:"" for x in request.variables},request.channel));return CommunicationRepository.create_template(request.model_dump())
@router.patch("/communication-templates/{template_id}")
async def update_template(template_id:str,request:TemplatePatch):return required(CommunicationRepository.update_template(template_id,request.model_dump(exclude_unset=True)))
@router.delete("/communication-templates/{template_id}")
async def delete_template(template_id:str):CommunicationRepository.delete_template(template_id);return {"deleted":True}
@router.post("/communication-templates/{template_id}/preview")
async def preview_template(template_id:str,request:PreviewRequest):return safe(lambda:CommunicationService.preview_template(required(CommunicationRepository.template(template_id)),request.variables))

@router.get("/properties/{property_id}/communications")
async def messages(property_id:str):return CommunicationRepository.list_messages(property_id)
@router.post("/properties/{property_id}/communications/draft")
async def create_draft(property_id:str,request:DraftRequest):require_permission("communications.draft");return safe(lambda:CommunicationService.create_draft(property_id,request.model_dump()))
@router.patch("/properties/{property_id}/communications/{message_id}")
async def update_message(property_id:str,message_id:str,request:MessagePatch):return required(CommunicationRepository.update_message(property_id,message_id,request.model_dump(exclude_unset=True)))
@router.delete("/properties/{property_id}/communications/{message_id}")
async def delete_message(property_id:str,message_id:str):CommunicationRepository.delete_message(property_id,message_id);CrmRepository.activity(property_id,"communication_draft_deleted","message",message_id,"Communication draft deleted");return {"deleted":True}
@router.post("/properties/{property_id}/communications/{message_id}/preview")
async def preview_message(property_id:str,message_id:str):
 message=required(CommunicationRepository.message(property_id,message_id));return {"subject":message.get("subject"),"body":message["body"],"variables":message.get("rendered_variables",{}),"consent_snapshot":message.get("consent_snapshot",{})}
@router.post("/properties/{property_id}/communications/{message_id}/send")
async def send_message(property_id:str,message_id:str,data:SendRequest,request:Request):require_permission("communications.send");return protected_operation(request,"communication-send",{"property_id":property_id,"message_id":message_id,**data.model_dump()},lambda:required(CommunicationService.send(property_id,message_id,data.confirm_send)))
@router.post("/properties/{property_id}/communications/{message_id}/cancel")
async def cancel_message(property_id:str,message_id:str):
 row=required(CommunicationRepository.update_message(property_id,message_id,{"status":"cancelled"}));CrmRepository.activity(property_id,"communication_cancelled","message",message_id,"Communication cancelled");return row
@router.patch("/properties/{property_id}/contacts/{contact_id}/consent")
async def update_consent(property_id:str,contact_id:str,request:ConsentPatch):
 row=required(CrmRepository.update("contacts",property_id,contact_id,request.model_dump(exclude_unset=True)));CrmRepository.activity(property_id,"communication_consent_updated","contact",contact_id,"Communication consent updated",metadata={"fields":list(request.model_dump(exclude_unset=True))});return row
