import unittest
from types import SimpleNamespace
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app
from app.providers.communications import ConsoleEmailProvider,EmailProvider,SmsProvider
from app.services.communication_service import CommunicationService as Service

SETTINGS=SimpleNamespace(COMMUNICATIONS_ENABLED=False,ALLOW_CONSOLE_DELIVERY=False,EMAIL_PROVIDER="console",SMS_PROVIDER="console",COMMUNICATION_BUSINESS_NAME="PI Homes",COMMUNICATION_SMS_OPT_OUT_TEXT="Reply STOP to opt out.")
CONTACT={"contact_id":"c1","email_consent_status":"consented","sms_consent_status":"consented","do_not_contact":False}
MESSAGE={"message_id":"m1","property_id":"p1","contact_id":"c1","channel":"email","status":"draft","subject":"Hi","body":"Body","consent_snapshot":{}}
class CommunicationTest(unittest.TestCase):
 def test_deterministic_template_rendering(self):
  with patch("app.services.communication_service.get_settings",return_value=SETTINGS):
   result=Service.render("Hi {{seller_first_name}}","Regarding {{property_address}}",{"seller_first_name":"Sam","property_address":"1 Main"},"email")
  self.assertEqual(result["subject"],"Hi Sam");self.assertEqual(result["variables"],{"property_address":"1 Main","seller_first_name":"Sam"})
 def test_unknown_variable_rejected(self):
  with self.assertRaisesRegex(ValueError,"Unknown template variables"):Service.render(None,"Hi {{secret_token}}",{},"email")
 def test_sms_appends_identification_and_opt_out(self):
  with patch("app.services.communication_service.get_settings",return_value=SETTINGS):result=Service.render(None,"Hello",{},"sms")
  self.assertIn("PI Homes",result["body"]);self.assertIn("STOP",result["body"])
 def test_sms_consent_blocking(self):
  for status in ("unknown","opted_out","prohibited"):self.assertIn(status,Service.block_reason({"sms_consent_status":status},"sms"))
 def test_email_opt_out_and_do_not_contact_blocking(self):
  self.assertIn("opted_out",Service.block_reason({"email_consent_status":"opted_out"},"email"));self.assertIn("do not contact",Service.block_reason({"do_not_contact":True},"email"))
 def test_draft_preserves_consent_and_creates_activity(self):
  with patch("app.services.communication_service.CrmRepository.get",return_value=CONTACT),patch("app.services.communication_service.CommunicationRepository.template",return_value=None),patch("app.services.communication_service.CommunicationRepository.create_message",side_effect=lambda x:{"message_id":"m1",**x}) as create,patch("app.services.communication_service.CrmRepository.activity") as activity,patch.object(Service,"notify"):
   row=Service.create_draft("p1",{"contact_id":"c1","channel":"email","subject":"Hi","body":"Body","variables":{}})
  self.assertEqual(row["status"],"draft");self.assertEqual(create.call_args.args[0]["consent_snapshot"]["email_consent_status"],"consented");activity.assert_called_once()
 def test_communications_disabled_and_confirmation_blocking(self):
  with patch("app.services.communication_service.CommunicationRepository.message",return_value=MESSAGE),patch("app.services.communication_service.CrmRepository.get",return_value=CONTACT),patch("app.services.communication_service.get_settings",return_value=SETTINGS),patch("app.services.communication_service.CommunicationRepository.update_message",side_effect=lambda p,m,d:{**MESSAGE,**d}),patch("app.services.communication_service.CrmRepository.activity"),patch.object(Service,"notify"):
   self.assertIn("confirmation",Service.send("p1","m1",False)["failure_reason"].lower());self.assertIn("disabled",Service.send("p1","m1",True)["failure_reason"].lower())
 def test_console_provider_interface_and_no_external_delivery(self):
  provider=ConsoleEmailProvider(False);self.assertIsInstance(provider,EmailProvider);self.assertFalse(provider.validate_configuration()[0])
  with self.assertRaises(RuntimeError):provider.send(MESSAGE)
 def test_failed_send_creates_notification(self):
  enabled=SimpleNamespace(**{**SETTINGS.__dict__,"COMMUNICATIONS_ENABLED":True,"ALLOW_CONSOLE_DELIVERY":True})
  class Failing:
   name="test" 
   def validate_configuration(self):return True,None
   def send(self,message):raise RuntimeError("provider failed")
  with patch("app.services.communication_service.CommunicationRepository.message",return_value=MESSAGE),patch("app.services.communication_service.CrmRepository.get",return_value=CONTACT),patch("app.services.communication_service.get_settings",return_value=enabled),patch.object(Service,"provider",return_value=Failing()),patch("app.services.communication_service.CommunicationRepository.update_message",side_effect=lambda p,m,d:{**MESSAGE,**d}),patch("app.services.communication_service.CrmRepository.activity"),patch.object(Service,"notify") as notify:
   row=Service.send("p1","m1",True)
  self.assertEqual(row["status"],"failed");self.assertEqual(notify.call_args.args[2],"failed_message")
 def test_draft_crud_and_history_endpoints(self):
  client=TestClient(app)
  with patch("app.routers.communications.CommunicationRepository.list_messages",return_value=[MESSAGE]):self.assertEqual(len(client.get("/properties/p1/communications").json()),1)
  with patch("app.routers.communications.CommunicationService.create_draft",return_value=MESSAGE):self.assertEqual(client.post("/properties/p1/communications/draft",json={"contact_id":"c1","channel":"email","subject":"Hi","body":"Body"}).status_code,200)
  with patch("app.routers.communications.CommunicationRepository.delete_message"),patch("app.routers.communications.CrmRepository.activity"):self.assertTrue(client.delete("/properties/p1/communications/m1").json()["deleted"])
 def test_provider_base_contracts_are_abstract(self):
  self.assertTrue(hasattr(EmailProvider,"send"));self.assertTrue(hasattr(SmsProvider,"validate_configuration"))
 def test_routes_registered(self):
  paths=set(app.openapi()["paths"])
  for path in ("/communication-templates","/communication-templates/{template_id}/preview","/properties/{property_id}/communications","/properties/{property_id}/communications/draft","/properties/{property_id}/communications/{message_id}/send","/properties/{property_id}/contacts/{contact_id}/consent"):self.assertIn(path,paths)
if __name__=="__main__":unittest.main()
