from datetime import datetime,timezone
from app.infrastructure.database.crm_repository import CrmRepository
from app.infrastructure.database.property_repository import PropertyRepository

class CrmService:
 @staticmethod
 def now(): return datetime.now(timezone.utc).isoformat()
 @classmethod
 def create(cls,kind,property_id,data):
  if kind=="contacts" and data.get("is_primary"): CrmRepository.clear_primary(property_id)
  row=CrmRepository.create(kind,property_id,data); CrmRepository.activity(property_id,f"{kind[:-1]}_created",kind[:-1],row[CrmRepository.IDS[kind]],f"{kind[:-1].replace('_',' ').title()} created")
  return row
 @classmethod
 def update(cls,kind,property_id,entity_id,data):
  if kind=="contacts" and data.get("is_primary"): CrmRepository.clear_primary(property_id)
  return CrmRepository.update(kind,property_id,entity_id,data)
 @classmethod
 def set_primary(cls,property_id,contact_id):
  CrmRepository.clear_primary(property_id); row=CrmRepository.update("contacts",property_id,contact_id,{"is_primary":True})
  if row: CrmRepository.activity(property_id,"primary_contact_changed","contact",contact_id,"Primary seller contact changed")
  return row
 @classmethod
 def complete_task(cls,property_id,task_id,complete=True):
  row=CrmRepository.update("tasks",property_id,task_id,{"status":"completed" if complete else "open","completed_at":cls.now() if complete else None})
  if row: CrmRepository.activity(property_id,"task_completed" if complete else "task_reopened","task",task_id,"Task completed" if complete else "Task reopened")
  return row
 @classmethod
 def pin_note(cls,property_id,note_id):
  note=CrmRepository.get("notes",property_id,note_id); return CrmRepository.update("notes",property_id,note_id,{"is_pinned":not note.get("is_pinned",False)}) if note else None
 @classmethod
 def workflow(cls,property_id):
  prop=PropertyRepository.get(property_id); return {"property_id":property_id,"current_stage":(prop or {}).get("workflow_stage") or "NEW_LEAD","assigned_to":(prop or {}).get("crm_assigned_to")} if prop else None
 @classmethod
 def change_stage(cls,property_id,to_stage,reason,changed_by):
  current=cls.workflow(property_id)
  if not current:return None
  old=current["current_stage"]; PropertyRepository.update(property_id,{"workflow_stage":to_stage})
  history=CrmRepository.add_history({"property_id":property_id,"from_stage":old,"to_stage":to_stage,"reason":reason,"changed_by":changed_by})
  CrmRepository.activity(property_id,"workflow_stage_changed","workflow",history["history_id"],f"Stage changed from {old} to {to_stage}",reason,{"from_stage":old,"to_stage":to_stage,"changed_by":changed_by})
  return {"property_id":property_id,"current_stage":to_stage,"previous_stage":old,"reason":reason,"changed_by":changed_by}
 @classmethod
 def record_sent_offer(cls,property_id,data):
  if not data.get("sent_at"): data["sent_at"]=cls.now()
  row=CrmRepository.create("sent_offers",property_id,data)
  CrmRepository.activity(property_id,"offer_sent","sent_offer",row["sent_offer_id"],f"Offer recorded as sent: ${row['offer_amount']:,.0f}",metadata={"offer_analysis_id":row.get("offer_analysis_id"),"delivery_method":row.get("delivery_method")})
  return row
 @staticmethod
 def is_overdue(row,now=None):
  if row.get("status") in ("completed","cancelled") or not row.get("due_at"): return False
  try:return datetime.fromisoformat(str(row["due_at"]).replace("Z","+00:00")) < (now or datetime.now(timezone.utc))
  except (ValueError,TypeError):return False
