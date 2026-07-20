from datetime import datetime,timezone,timedelta
from fastapi import APIRouter,HTTPException
from app.infrastructure.database.crm_repository import CrmRepository
from app.infrastructure.database.property_repository import PropertyRepository
from app.schemas.crm import ContactInput,ContactPatch,DeadlineInput,DeadlinePatch,NoteInput,NotePatch,SentOfferInput,SentOfferPatch,StageChange,TaskInput,TaskPatch
from app.services.crm_service import CrmService

router=APIRouter(tags=["Acquisition CRM"])

def required(value,message="CRM record was not found."):
 if not value: raise HTTPException(404,message)
 return value

@router.get("/properties/{property_id}/contacts")
async def contacts(property_id:str): return CrmRepository.list("contacts",property_id)
@router.post("/properties/{property_id}/contacts")
async def create_contact(property_id:str,request:ContactInput): return CrmService.create("contacts",property_id,request.model_dump())
@router.patch("/properties/{property_id}/contacts/{contact_id}")
async def update_contact(property_id:str,contact_id:str,request:ContactPatch): return required(CrmService.update("contacts",property_id,contact_id,request.model_dump(exclude_unset=True)))
@router.delete("/properties/{property_id}/contacts/{contact_id}")
async def delete_contact(property_id:str,contact_id:str): CrmRepository.delete("contacts",property_id,contact_id); return {"deleted":True}
@router.post("/properties/{property_id}/contacts/{contact_id}/primary")
async def primary_contact(property_id:str,contact_id:str): return required(CrmService.set_primary(property_id,contact_id))

@router.get("/properties/{property_id}/tasks")
async def tasks(property_id:str):
 now=datetime.now(timezone.utc); return [{**x,"is_overdue":CrmService.is_overdue(x,now)} for x in CrmRepository.list("tasks",property_id)]
@router.post("/properties/{property_id}/tasks")
async def create_task(property_id:str,request:TaskInput): return CrmService.create("tasks",property_id,request.model_dump())
@router.patch("/properties/{property_id}/tasks/{task_id}")
async def update_task(property_id:str,task_id:str,request:TaskPatch): return required(CrmService.update("tasks",property_id,task_id,request.model_dump(exclude_unset=True)))
@router.delete("/properties/{property_id}/tasks/{task_id}")
async def delete_task(property_id:str,task_id:str): CrmRepository.delete("tasks",property_id,task_id); return {"deleted":True}
@router.post("/properties/{property_id}/tasks/{task_id}/complete")
async def complete_task(property_id:str,task_id:str): return required(CrmService.complete_task(property_id,task_id))
@router.post("/properties/{property_id}/tasks/{task_id}/reopen")
async def reopen_task(property_id:str,task_id:str): return required(CrmService.complete_task(property_id,task_id,False))

@router.get("/properties/{property_id}/notes")
async def notes(property_id:str): return CrmRepository.list("notes",property_id)
@router.post("/properties/{property_id}/notes")
async def create_note(property_id:str,request:NoteInput): return CrmService.create("notes",property_id,request.model_dump())
@router.patch("/properties/{property_id}/notes/{note_id}")
async def update_note(property_id:str,note_id:str,request:NotePatch): return required(CrmService.update("notes",property_id,note_id,request.model_dump(exclude_unset=True)))
@router.delete("/properties/{property_id}/notes/{note_id}")
async def delete_note(property_id:str,note_id:str): CrmRepository.delete("notes",property_id,note_id); return {"deleted":True}
@router.post("/properties/{property_id}/notes/{note_id}/pin")
async def pin_note(property_id:str,note_id:str): return required(CrmService.pin_note(property_id,note_id))

@router.get("/properties/{property_id}/workflow")
async def workflow(property_id:str): return required(CrmService.workflow(property_id),"Property was not found.")
@router.post("/properties/{property_id}/workflow/stage")
async def change_stage(property_id:str,request:StageChange): return required(CrmService.change_stage(property_id,request.to_stage,request.reason,request.changed_by),"Property was not found.")
@router.get("/properties/{property_id}/workflow/history")
async def workflow_history(property_id:str): return CrmRepository.history(property_id)
@router.get("/properties/{property_id}/activity")
async def activity(property_id:str): return CrmRepository.activities(property_id)

@router.get("/properties/{property_id}/deadlines")
async def deadlines(property_id:str): return CrmRepository.list("deadlines",property_id)
@router.post("/properties/{property_id}/deadlines")
async def create_deadline(property_id:str,request:DeadlineInput): return CrmService.create("deadlines",property_id,request.model_dump())
@router.patch("/properties/{property_id}/deadlines/{deadline_id}")
async def update_deadline(property_id:str,deadline_id:str,request:DeadlinePatch): return required(CrmService.update("deadlines",property_id,deadline_id,request.model_dump(exclude_unset=True)))
@router.delete("/properties/{property_id}/deadlines/{deadline_id}")
async def delete_deadline(property_id:str,deadline_id:str): CrmRepository.delete("deadlines",property_id,deadline_id); return {"deleted":True}

@router.get("/properties/{property_id}/sent-offers")
async def sent_offers(property_id:str): return CrmRepository.list("sent_offers",property_id)
@router.post("/properties/{property_id}/sent-offers")
async def create_sent_offer(property_id:str,request:SentOfferInput): return CrmService.record_sent_offer(property_id,request.model_dump())
@router.patch("/properties/{property_id}/sent-offers/{sent_offer_id}")
async def update_sent_offer(property_id:str,sent_offer_id:str,request:SentOfferPatch): return required(CrmService.update("sent_offers",property_id,sent_offer_id,request.model_dump(exclude_unset=True)))

@router.get("/crm/dashboard")
async def crm_dashboard():
 properties=PropertyRepository.get_all(); tasks=CrmRepository.all("tasks"); contacts=CrmRepository.all("contacts")
 now=datetime.now(timezone.utc); today=now.date(); week=today+timedelta(days=7)
 open_tasks=[x for x in tasks if x.get("status") not in ("completed","cancelled")]
 due_dates=[]
 for task in open_tasks:
  try: due_dates.append((task,datetime.fromisoformat(str(task.get("due_at")).replace("Z","+00:00"))))
  except (ValueError,TypeError): pass
 stages={stage:sum(1 for p in properties if (p.get("workflow_stage") or "NEW_LEAD")==stage) for stage in ("NEW_LEAD","RESEARCH","READY_TO_OFFER","OFFER_SENT","NEGOTIATING","UNDER_CONTRACT","MARKETING","SOLD","ARCHIVED")}
 summaries={}
 for prop in properties:
  pid=prop["property_id"]; property_tasks=sorted((x for x in open_tasks if x["property_id"]==pid and x.get("due_at")),key=lambda x:x["due_at"])
  primary=next((x for x in contacts if x["property_id"]==pid and x.get("is_primary")),None)
  summaries[pid]={"current_stage":prop.get("workflow_stage") or "NEW_LEAD","assigned_to":prop.get("crm_assigned_to"),"next_follow_up":property_tasks[0].get("due_at") if property_tasks else None,"has_overdue":any(CrmService.is_overdue(x,now) for x in property_tasks),"primary_seller_name":" ".join(filter(None,[(primary or {}).get("first_name"),(primary or {}).get("last_name")])) or (primary or {}).get("company_name")}
 return {"leads_by_stage":stages,"overdue_tasks":sum(1 for x in open_tasks if CrmService.is_overdue(x,now)),"due_today":sum(1 for _,d in due_dates if d.date()==today),"due_this_week":sum(1 for _,d in due_dates if today<=d.date()<=week),"under_contract":stages["UNDER_CONTRACT"],"offers_sent":stages["OFFER_SENT"],"follow_ups_needed":len(open_tasks),"property_summaries":summaries}
