from fastapi import APIRouter,HTTPException,Query
from app.infrastructure.database.notification_repository import NotificationRepository
from app.services.notification_service import NotificationService
router=APIRouter(tags=["Notifications"])

@router.get("/notifications")
async def notifications(unread_only:bool=False,severity:str|None=None,notification_type:str|None=None,property_id:str|None=None,due_from:str|None=None,due_to:str|None=None,include_dismissed:bool=True,status:str|None=None):return NotificationRepository.list(locals())
@router.get("/notifications/unread-count")
async def unread_count():return {"unread_count":NotificationRepository.unread_count()}
@router.post("/notifications/scan")
async def scan_all():return NotificationService.scan_all()
@router.post("/properties/{property_id}/notifications/scan")
async def scan_property(property_id:str):
 result=NotificationService.scan_property(property_id)
 if not result:raise HTTPException(404,"Property was not found.")
 return result
def status(notification_id,status):
 result=NotificationService.set_status(notification_id,status)
 if not result:raise HTTPException(404,"Notification was not found.")
 return result
@router.post("/notifications/{notification_id}/read")
async def read(notification_id:str):return status(notification_id,"read")
@router.post("/notifications/{notification_id}/unread")
async def unread(notification_id:str):return status(notification_id,"unread")
@router.post("/notifications/{notification_id}/dismiss")
async def dismiss(notification_id:str):return status(notification_id,"dismissed")
@router.post("/notifications/read-all")
async def read_all():
 rows=NotificationRepository.list({"unread_only":True})
 for row in rows:NotificationService.set_status(row["notification_id"],"read")
 return {"updated":len(rows)}
