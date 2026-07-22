from datetime import datetime,timedelta,timezone
import unittest
from unittest.mock import patch
from app.services.notification_service import NotificationService as Service
from app.jobs.notification_scan import main,run_once

NOW=datetime(2026,7,20,12,tzinfo=timezone.utc);PROP={"property_id":"p1","workflow_stage":"NEW_LEAD","created_at":(NOW-timedelta(days=10)).isoformat()}
def task(delta):return {"task_id":"t1","title":"Call seller","status":"open","due_at":(NOW+delta).isoformat()}
def deadline(delta,kind="closing"):return {"deadline_id":"d1","title":"Close","status":"open","deadline_type":kind,"due_at":(NOW+delta).isoformat()}
class NotificationTest(unittest.TestCase):
 def evaluate(self,tasks=None,deadlines=None,offers=None,prop=None,contacts=None,activities=None):return Service.evaluate(prop or PROP,tasks or [],deadlines or [],offers or [],contacts if contacts is not None else [{}],activities or [],NOW)
 def test_overdue_due_today_and_due_soon_followups(self):
  self.assertEqual(self.evaluate([task(timedelta(hours=-1))])[0]["notification_type"],"overdue_follow_up");self.assertEqual(self.evaluate([task(timedelta(hours=2))])[0]["notification_type"],"follow_up_due_today");self.assertEqual(self.evaluate([task(timedelta(days=2))])[0]["notification_type"],"follow_up_due_soon")
 def test_overdue_deadline(self):self.assertEqual(self.evaluate(deadlines=[deadline(timedelta(hours=-1))])[0]["notification_type"],"deadline_overdue")
 def test_offer_warning_and_expiration_have_distinct_keys(self):
  base={"sent_offer_id":"o1","offer_amount":100000,"status":"sent"};warning=self.evaluate(offers=[{**base,"expiration_at":(NOW+timedelta(hours=12)).isoformat()}])[0];expired=self.evaluate(offers=[{**base,"expiration_at":(NOW-timedelta(hours=1)).isoformat()}])[0];self.assertEqual(warning["notification_type"],"offer_expiring");self.assertNotEqual(warning["dedupe_key"],expired["dedupe_key"])
 def test_stale_lead_and_contact_needed(self):
  kinds={x["notification_type"] for x in self.evaluate(contacts=[],activities=[])};self.assertIn("stale_lead",kinds);self.assertIn("seller_contact_needed",kinds)
 def test_under_contract_escalation(self):
  result=self.evaluate(deadlines=[deadline(timedelta(days=2),"inspection")],prop={**PROP,"workflow_stage":"UNDER_CONTRACT"})[0];self.assertEqual(result["notification_type"],"under_contract_deadline_risk");self.assertEqual(result["severity"],"critical")
 def test_sold_archived_excluded(self):
  for stage in ("SOLD","ARCHIVED"):self.assertEqual(Service.evaluate({**PROP,"workflow_stage":stage},[task(timedelta(days=-1))],[],[],[],[],NOW),[])
 def test_deduplication_and_dismissal(self):
  candidate=self.evaluate([task(timedelta(days=-1))])[0];existing={"notification_id":"n1","dedupe_key":candidate["dedupe_key"],"status":"dismissed"}
  with patch("app.services.notification_service.NotificationRepository.property_records",return_value=[existing]),patch("app.services.notification_service.NotificationRepository.create") as create,patch("app.services.notification_service.NotificationRepository.update") as update:Service.reconcile("p1",[candidate]);create.assert_not_called();update.assert_not_called()
 def test_state_change_regenerates(self):
  first=self.evaluate([task(timedelta(days=-1))])[0];second=self.evaluate([{**task(timedelta(days=-1)),"due_at":(NOW-timedelta(days=2)).isoformat()}])[0];self.assertNotEqual(first["dedupe_key"],second["dedupe_key"])
 def test_read_unread_dismiss(self):
  with patch("app.services.notification_service.NotificationRepository.update",side_effect=lambda nid,data:{"notification_id":nid,**data}):self.assertEqual(Service.set_status("n","read")["status"],"read");self.assertIsNone(Service.set_status("n","unread")["read_at"]);self.assertEqual(Service.set_status("n","dismissed")["status"],"dismissed")
 def test_all_property_scan(self):
  with patch("app.services.notification_service.PropertyRepository.get_all",return_value=[{"property_id":"p1"},{"property_id":"p2"}]),patch.object(Service,"scan_property",side_effect=[{"created":1,"updated":0,"resolved":0},{"created":0,"updated":1,"resolved":1}]):result=Service.scan_all(NOW);self.assertEqual(result["properties_scanned"],2);self.assertEqual(result["created"],1)
 def test_scheduler_single_run(self):
  with patch("app.jobs.notification_scan.NotificationService.scan_all",return_value={"properties_scanned":1,"created":2,"updated":0,"resolved":0}) as scan:run_once();scan.assert_called_once()
