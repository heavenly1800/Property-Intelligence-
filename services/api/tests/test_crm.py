from datetime import datetime,timedelta,timezone
import unittest
from unittest.mock import patch,call
from fastapi.testclient import TestClient
from app.main import app
from app.services.crm_service import CrmService

class CrmServiceTest(unittest.TestCase):
 def test_primary_contact_clears_existing_then_creates(self):
  with patch("app.services.crm_service.CrmRepository.clear_primary") as clear,patch("app.services.crm_service.CrmRepository.create",return_value={"contact_id":"c1","is_primary":True}) as create,patch("app.services.crm_service.CrmRepository.activity"):
   CrmService.create("contacts","PROP-001",{"first_name":"Seller","is_primary":True});clear.assert_called_once_with("PROP-001");create.assert_called_once()
 def test_contact_crud_endpoint_contracts(self):
  client=TestClient(app)
  with patch("app.routers.crm.CrmRepository.list",return_value=[]): self.assertEqual(client.get("/properties/PROP-001/contacts").status_code,200)
  with patch("app.routers.crm.CrmService.create",return_value={"contact_id":"c1"}): self.assertEqual(client.post("/properties/PROP-001/contacts",json={"first_name":"A"}).status_code,200)
  with patch("app.routers.crm.CrmService.update",return_value={"contact_id":"c1"}): self.assertEqual(client.patch("/properties/PROP-001/contacts/c1",json={"phone":"1"}).status_code,200)
  with patch("app.routers.crm.CrmRepository.delete",return_value=[]): self.assertTrue(client.delete("/properties/PROP-001/contacts/c1").json()["deleted"])
 def test_note_pinning_toggles(self):
  with patch("app.services.crm_service.CrmRepository.get",return_value={"note_id":"n1","is_pinned":False}),patch("app.services.crm_service.CrmRepository.update",return_value={"note_id":"n1","is_pinned":True}) as update:
   self.assertTrue(CrmService.pin_note("PROP-001","n1")["is_pinned"]);self.assertTrue(update.call_args.args[3]["is_pinned"])
 def test_task_completion_and_reopening(self):
  with patch("app.services.crm_service.CrmRepository.update",side_effect=lambda kind,pid,eid,data:{"task_id":eid,**data}) as update,patch("app.services.crm_service.CrmRepository.activity"):
   self.assertEqual(CrmService.complete_task("PROP-001","t1")["status"],"completed");self.assertEqual(CrmService.complete_task("PROP-001","t1",False)["status"],"open");self.assertIsNone(update.call_args.args[3]["completed_at"])
 def test_overdue_detection(self):
  past=(datetime.now(timezone.utc)-timedelta(hours=1)).isoformat();future=(datetime.now(timezone.utc)+timedelta(hours=1)).isoformat()
  self.assertTrue(CrmService.is_overdue({"status":"open","due_at":past}));self.assertFalse(CrmService.is_overdue({"status":"completed","due_at":past}));self.assertFalse(CrmService.is_overdue({"status":"open","due_at":future}))
 def test_deadline_endpoint_handling(self):
  client=TestClient(app);payload={"deadline_type":"closing","title":"Close","due_at":"2026-08-01T12:00:00Z"}
  with patch("app.routers.crm.CrmService.create",return_value={"deadline_id":"d1",**payload}): self.assertEqual(client.post("/properties/PROP-001/deadlines",json=payload).status_code,200)
  with patch("app.routers.crm.CrmService.update",return_value={"deadline_id":"d1","status":"completed"}): self.assertEqual(client.patch("/properties/PROP-001/deadlines/d1",json={"status":"completed"}).status_code,200)
 def test_explicit_stage_change_writes_property_history_and_activity(self):
  with patch.object(CrmService,"workflow",return_value={"current_stage":"NEW_LEAD"}),patch("app.services.crm_service.PropertyRepository.update") as prop,patch("app.services.crm_service.CrmRepository.add_history",return_value={"history_id":"h1"}) as history,patch("app.services.crm_service.CrmRepository.activity") as activity:
   result=CrmService.change_stage("PROP-001","RESEARCH","Start diligence","user")
   self.assertEqual(result["current_stage"],"RESEARCH");prop.assert_called_once_with("PROP-001",{"workflow_stage":"RESEARCH"});history.assert_called_once();activity.assert_called_once()
 def test_sent_offer_creates_activity_without_stage_change(self):
  with patch("app.services.crm_service.CrmRepository.create",return_value={"sent_offer_id":"s1","offer_amount":570000,"offer_analysis_id":"o1"}),patch("app.services.crm_service.CrmRepository.activity") as activity,patch("app.services.crm_service.PropertyRepository.update") as prop:
   row=CrmService.record_sent_offer("PROP-001",{"offer_amount":570000,"offer_analysis_id":"o1"});self.assertEqual(row["offer_analysis_id"],"o1");activity.assert_called_once();prop.assert_not_called()
 def test_archived_properties_remain_in_dashboard_and_counts_are_correct(self):
  client=TestClient(app);now=datetime.now(timezone.utc);properties=[{"property_id":"p1","workflow_stage":"ARCHIVED"},{"property_id":"p2","workflow_stage":"UNDER_CONTRACT"},{"property_id":"p3","workflow_stage":"OFFER_SENT"}];tasks=[{"property_id":"p1","task_id":"t1","status":"open","due_at":(now-timedelta(days=1)).isoformat()},{"property_id":"p2","task_id":"t2","status":"open","due_at":(now+timedelta(hours=1)).isoformat()}]
  with patch("app.routers.crm.PropertyRepository.get_all",return_value=properties),patch("app.routers.crm.CrmRepository.all",side_effect=[tasks,[]]):
   data=client.get("/crm/dashboard").json();self.assertEqual(data["leads_by_stage"]["ARCHIVED"],1);self.assertEqual(data["under_contract"],1);self.assertEqual(data["offers_sent"],1);self.assertEqual(data["overdue_tasks"],1);self.assertIn("p1",data["property_summaries"])
 def test_required_routes_registered(self):
  paths=set(app.openapi()["paths"])
  for suffix in ("contacts","tasks","notes","workflow","workflow/stage","workflow/history","activity","deadlines","sent-offers"): self.assertIn(f"/properties/{{property_id}}/{suffix}",paths)

if __name__=="__main__":unittest.main()
