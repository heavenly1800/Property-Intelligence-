import json
from datetime import datetime,timedelta,timezone
from app.core.settings import get_settings
from app.infrastructure.database.crm_repository import CrmRepository
from app.infrastructure.database.notification_repository import NotificationRepository
from app.infrastructure.database.property_repository import PropertyRepository

class NotificationService:
 CONTACT_ACTIVITY={"contact_created","primary_contact_changed","note_created","offer_sent"}
 CRITICAL_DEADLINES={"inspection","due_diligence","earnest_money","assignment","closing"}
 @staticmethod
 def dt(value):
  if not value:return None
  try:
   parsed=datetime.fromisoformat(str(value).replace("Z","+00:00"));return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed.astimezone(timezone.utc)
  except (ValueError,TypeError):return None
 @staticmethod
 def key(kind,entity_id,state):return f"{kind}:{entity_id}:{state}"
 @classmethod
 def candidate(cls,property_id,kind,severity,title,message,entity_type,entity_id,due,state,metadata=None):
  return {"property_id":property_id,"notification_type":kind,"severity":severity,"title":title,"message":message,"related_entity_type":entity_type,"related_entity_id":str(entity_id) if entity_id else None,"scheduled_for":due.isoformat() if due else None,"dedupe_key":cls.key(kind,entity_id or property_id,state),"metadata":metadata or {}}
 @classmethod
 def evaluate(cls,prop,tasks,deadlines,offers,contacts,activities,now=None):
  now=now or datetime.now(timezone.utc);s=get_settings();pid=prop["property_id"];stage=prop.get("workflow_stage") or "NEW_LEAD";out=[]
  if stage in ("SOLD","ARCHIVED"):return out
  today=now.date()
  for task in tasks:
   if task.get("status") in ("completed","cancelled") or not (due:=cls.dt(task.get("due_at"))):continue
   delta=(due.date()-today).days;entity=task["task_id"];state=due.isoformat()
   if due<now:kind,severity="overdue_follow_up","high"
   elif delta==0:kind,severity="follow_up_due_today","warning"
   elif delta<=s.NOTIFICATION_FOLLOW_UP_DUE_SOON_DAYS:kind,severity="follow_up_due_soon","info"
   else:continue
   out.append(cls.candidate(pid,kind,severity,task.get("title") or "Seller follow-up",f"Follow-up is {('overdue' if due<now else 'due '+due.strftime('%b %d'))}.","task",entity,due,state,{"due_at":due.isoformat()}))
  for deadline in deadlines:
   if deadline.get("status") in ("completed","cancelled") or not (due:=cls.dt(deadline.get("due_at"))):continue
   delta=(due.date()-today).days;critical=stage=="UNDER_CONTRACT" and deadline.get("deadline_type") in cls.CRITICAL_DEADLINES and delta<=s.NOTIFICATION_UNDER_CONTRACT_CRITICAL_WINDOW_DAYS
   if due<now:kind,severity=("under_contract_deadline_risk","critical") if critical else ("deadline_overdue","high")
   elif delta==0:kind,severity=("under_contract_deadline_risk","critical") if critical else ("deadline_due_today","warning")
   elif delta<=s.NOTIFICATION_DEADLINE_DUE_SOON_DAYS:kind,severity=("under_contract_deadline_risk","critical") if critical else ("deadline_due_soon","info")
   else:continue
   out.append(cls.candidate(pid,kind,severity,deadline.get("title") or "Property deadline",f"{deadline.get('deadline_type','Deadline').replace('_',' ').title()} is due {due.strftime('%b %d, %Y')}.","deadline",deadline["deadline_id"],due,due.isoformat(),{"deadline_type":deadline.get("deadline_type")}))
  warning=timedelta(hours=s.NOTIFICATION_OFFER_EXPIRATION_WARNING_HOURS)
  for offer in offers:
   if offer.get("status") in ("expired","rejected","withdrawn") or not (due:=cls.dt(offer.get("expiration_at"))):continue
   if due<=now:state,severity="expired","high"
   elif due-now<=warning:state,severity="warning","warning"
   else:continue
   out.append(cls.candidate(pid,"offer_expiring",severity,"Offer expired" if state=="expired" else "Offer expiring soon",f"The {offer.get('offer_amount',0):,.0f} offer {'expired' if state=='expired' else 'expires '+due.strftime('%b %d at %I:%M %p')}.","sent_offer",offer["sent_offer_id"],due,f"{due.isoformat()}:{state}"))
  if not contacts:out.append(cls.candidate(pid,"seller_contact_needed","warning","Seller contact needed","No seller contact is recorded for this active property.","property",pid,None,"no-contact"))
  thresholds={};
  try:thresholds=json.loads(s.NOTIFICATION_STALE_LEAD_DAYS_JSON or "{}")
  except json.JSONDecodeError:pass
  stale_days=int(thresholds.get(stage,s.NOTIFICATION_STALE_LEAD_DAYS));contact_events=[cls.dt(x.get("occurred_at")) for x in activities if x.get("activity_type") in cls.CONTACT_ACTIVITY];contact_events=[x for x in contact_events if x]
  baseline=max(contact_events) if contact_events else cls.dt(prop.get("created_at"))
  if baseline and now-baseline>=timedelta(days=stale_days):out.append(cls.candidate(pid,"stale_lead","warning","Seller contact is stale",f"No seller-contact activity has been recorded for at least {stale_days} days.","property",pid,None,f"{baseline.date()}:{stale_days}",{"last_contact_at":baseline.isoformat(),"stale_days":stale_days}))
  return out
 @classmethod
 def reconcile(cls,property_id,candidates):
  existing=NotificationRepository.property_records(property_id);by_key={x["dedupe_key"]:x for x in existing};desired={x["dedupe_key"] for x in candidates};created=updated=resolved=0
  for item in candidates:
   old=by_key.get(item["dedupe_key"])
   if not old:NotificationRepository.create({**item,"status":"unread"});created+=1
   elif old.get("status") not in ("dismissed",):NotificationRepository.update(old["notification_id"],{k:v for k,v in item.items() if k not in ("property_id","dedupe_key")});updated+=1
  for old in existing:
   if old["dedupe_key"] not in desired and old.get("status") in ("unread","read"):NotificationRepository.update(old["notification_id"],{"status":"resolved"});resolved+=1
  return {"property_id":property_id,"created":created,"updated":updated,"resolved":resolved,"active":len(candidates)}
 @classmethod
 def scan_property(cls,property_id,now=None):
  prop=PropertyRepository.get(property_id)
  if not prop:return None
  candidates=cls.evaluate(prop,CrmRepository.list("tasks",property_id),CrmRepository.list("deadlines",property_id),CrmRepository.list("sent_offers",property_id),CrmRepository.list("contacts",property_id),CrmRepository.activities(property_id),now)
  return cls.reconcile(property_id,candidates)
 @classmethod
 def scan_all(cls,now=None):
  results=[cls.scan_property(p["property_id"],now) for p in PropertyRepository.get_all()];return {"properties_scanned":len(results),"created":sum(x["created"] for x in results if x),"updated":sum(x["updated"] for x in results if x),"resolved":sum(x["resolved"] for x in results if x),"results":results}
 @staticmethod
 def set_status(notification_id,status):
  now=datetime.now(timezone.utc).isoformat();data={"status":status}
  if status=="read":data["read_at"]=now
  if status=="unread":data["read_at"]=None
  if status=="dismissed":data["dismissed_at"]=now
  return NotificationRepository.update(notification_id,data)
