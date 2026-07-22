from datetime import datetime,timezone
from app.infrastructure.database.supabase import supabase
class CommunicationRepository:
 @staticmethod
 def templates():return supabase.table("communication_templates").select("*").order("template_name").execute().data
 @staticmethod
 def template(template_id):
  rows=supabase.table("communication_templates").select("*").eq("template_id",template_id).execute().data;return rows[0] if rows else None
 @staticmethod
 def create_template(data):return supabase.table("communication_templates").insert(data).execute().data[0]
 @staticmethod
 def update_template(template_id,data):
  rows=supabase.table("communication_templates").update({**data,"updated_at":datetime.now(timezone.utc).isoformat()}).eq("template_id",template_id).execute().data;return rows[0] if rows else None
 @staticmethod
 def delete_template(template_id):return supabase.table("communication_templates").delete().eq("template_id",template_id).execute().data
 @staticmethod
 def list_messages(property_id):return supabase.table("property_communications").select("*").eq("property_id",property_id).order("created_at",desc=True).execute().data
 @staticmethod
 def message(property_id,message_id):
  rows=supabase.table("property_communications").select("*").eq("property_id",property_id).eq("message_id",message_id).execute().data;return rows[0] if rows else None
 @staticmethod
 def create_message(data):return supabase.table("property_communications").insert(data).execute().data[0]
 @staticmethod
 def update_message(property_id,message_id,data):
  rows=supabase.table("property_communications").update({**data,"updated_at":datetime.now(timezone.utc).isoformat()}).eq("property_id",property_id).eq("message_id",message_id).execute().data;return rows[0] if rows else None
 @staticmethod
 def delete_message(property_id,message_id):return supabase.table("property_communications").delete().eq("property_id",property_id).eq("message_id",message_id).execute().data
