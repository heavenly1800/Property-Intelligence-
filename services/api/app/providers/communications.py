from abc import ABC,abstractmethod
class DeliveryProvider(ABC):
 name="base"
 @abstractmethod
 def send(self,message):raise NotImplementedError
 @abstractmethod
 def validate_configuration(self):raise NotImplementedError
 def normalize_status(self,status):return status
 def parse_webhook_event(self,event):return event
class EmailProvider(DeliveryProvider):pass
class SmsProvider(DeliveryProvider):pass
class ConsoleEmailProvider(EmailProvider):
 name="console"
 def __init__(self,allowed=False):self.allowed=allowed
 def validate_configuration(self):return (self.allowed,"Console delivery is disabled. Set ALLOW_CONSOLE_DELIVERY=true only for local preview delivery.")
 def send(self,message):
  if not self.allowed:raise RuntimeError("Console email delivery is disabled.")
  print(f"[SAFE EMAIL PREVIEW] message_id={message.get('message_id')} subject={message.get('subject','')[:80]}");return {"provider_message_id":f"console-email-{message['message_id']}","status":"sent"}
class ConsoleSmsProvider(SmsProvider):
 name="console"
 def __init__(self,allowed=False):self.allowed=allowed
 def validate_configuration(self):return (self.allowed,"Console delivery is disabled. Set ALLOW_CONSOLE_DELIVERY=true only for local preview delivery.")
 def send(self,message):
  if not self.allowed:raise RuntimeError("Console SMS delivery is disabled.")
  print(f"[SAFE SMS PREVIEW] message_id={message.get('message_id')} characters={len(message.get('body',''))}");return {"provider_message_id":f"console-sms-{message['message_id']}","status":"sent"}
