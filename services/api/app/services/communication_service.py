import re
from datetime import datetime,timezone
from app.core.settings import get_settings
from app.infrastructure.database.communication_repository import CommunicationRepository
from app.infrastructure.database.crm_repository import CrmRepository
from app.infrastructure.database.notification_repository import NotificationRepository
from app.infrastructure.database.property_repository import PropertyRepository
from app.providers.communications import ConsoleEmailProvider,ConsoleSmsProvider

class CommunicationService:
 APPROVED={"seller_first_name","seller_last_name","property_address","offer_amount","offer_expiration","follow_up_date","user_name","company_name","callback_number","custom_notes"};PATTERN=re.compile(r"{{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*}}")
 @classmethod
 def render(cls,subject,body,variables,channel=None):
  found=set(cls.PATTERN.findall((subject or "")+"\n"+(body or "")));unknown=found-cls.APPROVED
  if unknown:raise ValueError(f"Unknown template variables: {', '.join(sorted(unknown))}")
  replace=lambda text:cls.PATTERN.sub(lambda m:str(variables.get(m.group(1),"")),text or "")
  rendered_body=replace(body)
  if channel=="sms":
   s=get_settings();footer=f"{s.COMMUNICATION_BUSINESS_NAME}. {s.COMMUNICATION_SMS_OPT_OUT_TEXT}";rendered_body=f"{rendered_body.rstrip()}\n{footer}"
  return {"subject":replace(subject) or None,"body":rendered_body,"variables":{key:variables.get(key) for key in sorted(found)}}
 @staticmethod
 def consent_snapshot(contact):return {key:contact.get(key) for key in ("email_consent_status","email_consent_source","email_consent_at","sms_consent_status","sms_consent_source","sms_consent_at","sms_opted_out_at","email_opted_out_at","do_not_contact","preferred_contact_method","timezone")}
 @classmethod
 def block_reason(cls,contact,channel):
  if contact.get("do_not_contact"):return "Contact is marked do not contact."
  status=contact.get(f"{channel}_consent_status") or "unknown"
  if channel=="sms" and status in ("unknown","opted_out","prohibited"):return f"SMS consent status is {status}."
  if channel=="email" and status in ("opted_out","prohibited"):return f"Email consent status is {status}."
  return None
 @classmethod
 def preview_template(cls,template,variables):return cls.render(template.get("subject_template"),template["body_template"],variables,template["channel"])
 @classmethod
 def create_draft(cls,property_id,data):
  contact=CrmRepository.get("contacts",property_id,data["contact_id"])
  if not contact:raise ValueError("Seller contact was not found.")
  template=CommunicationRepository.template(data.get("template_id")) if data.get("template_id") else None
  if template and template["channel"]!=data["channel"]:raise ValueError("Template channel does not match draft channel.")
  rendered=cls.render((template or {}).get("subject_template") if template else data.get("subject"),(template or {}).get("body_template") if template else data.get("body") or "",data.get("variables") or {},data["channel"])
  row=CommunicationRepository.create_message({"property_id":property_id,"contact_id":data["contact_id"],"template_id":data.get("template_id"),"channel":data["channel"],"direction":"outbound","status":"draft","subject":rendered["subject"],"body":rendered["body"],"rendered_variables":rendered["variables"],"scheduled_for":data.get("scheduled_for"),"consent_snapshot":cls.consent_snapshot(contact),"related_offer_id":data.get("related_offer_id"),"related_task_id":data.get("related_task_id")})
  CrmRepository.activity(property_id,"communication_draft_created","message",row["message_id"],f"{data['channel'].upper()} draft created")
  cls.notify(property_id,row,"draft_awaiting_approval","info","Communication draft awaiting approval")
  if data.get("create_follow_up"):
   task=CrmRepository.create("tasks",property_id,{"contact_id":data["contact_id"],"title":data.get("follow_up_title") or f"Follow up on {data['channel']} draft","task_type":"follow_up","due_at":data.get("follow_up_due_at"),"priority":"normal","status":"open"});CommunicationRepository.update_message(property_id,row["message_id"],{"related_task_id":task["task_id"]});row["related_task_id"]=task["task_id"]
  return row
 @staticmethod
 def notify(property_id,message,kind,severity,title):
  key=f"{kind}:message:{message['message_id']}:{message.get('status')}";existing={x["dedupe_key"] for x in NotificationRepository.property_records(property_id)}
  if key not in existing:NotificationRepository.create({"property_id":property_id,"notification_type":kind,"severity":severity,"title":title,"message":message.get("failure_reason") or f"Message {message.get('status')}.","related_entity_type":"message","related_entity_id":message["message_id"],"dedupe_key":key,"status":"unread","metadata":{"channel":message.get("channel")}})
 @staticmethod
 def provider(channel):
  s=get_settings();return ConsoleEmailProvider(s.ALLOW_CONSOLE_DELIVERY) if channel=="email" else ConsoleSmsProvider(s.ALLOW_CONSOLE_DELIVERY)
 @classmethod
 def send(cls,property_id,message_id,confirmed):
  message=CommunicationRepository.message(property_id,message_id)
  if not message:return None
  contact=CrmRepository.get("contacts",property_id,message["contact_id"]);s=get_settings();reason=None
  if not confirmed:reason="Explicit send confirmation is required."
  elif message.get("status") not in ("draft","scheduled"):reason="Only draft or scheduled messages can be sent."
  elif not s.COMMUNICATIONS_ENABLED:reason="External communications are disabled. Set COMMUNICATIONS_ENABLED=true after provider and compliance review."
  elif (consent:=cls.block_reason(contact or {},message["channel"])):reason=consent
  configured_name=s.EMAIL_PROVIDER if message["channel"]=="email" else s.SMS_PROVIDER
  if not reason and configured_name!="console":reason=f"Configured {message['channel']} provider '{configured_name}' is not implemented."
  provider=cls.provider(message["channel"]);valid,provider_reason=provider.validate_configuration()
  if not reason and not valid:reason=provider_reason
  if reason:
   row=CommunicationRepository.update_message(property_id,message_id,{"status":"blocked","failure_reason":reason,"consent_snapshot":cls.consent_snapshot(contact or {})});CrmRepository.activity(property_id,"communication_blocked","message",message_id,"Communication send blocked",reason);cls.notify(property_id,row,"scheduled_message_blocked","high","Communication blocked");return row
  try:
   result=provider.send(message);row=CommunicationRepository.update_message(property_id,message_id,{"status":result["status"],"provider_name":provider.name,"provider_message_id":result["provider_message_id"],"sent_at":datetime.now(timezone.utc).isoformat(),"failure_reason":None});CrmRepository.activity(property_id,"communication_sent","message",message_id,"Communication sent");return row
  except Exception as exc:
   row=CommunicationRepository.update_message(property_id,message_id,{"status":"failed","failed_at":datetime.now(timezone.utc).isoformat(),"failure_reason":str(exc)});CrmRepository.activity(property_id,"communication_failed","message",message_id,"Communication failed",str(exc));cls.notify(property_id,row,"failed_message","critical","Communication failed");return row
