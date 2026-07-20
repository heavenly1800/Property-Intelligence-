from datetime import datetime,timezone
from app.infrastructure.database.supabase import supabase

class CrmRepository:
 TABLES={"contacts":"property_contacts","tasks":"property_follow_up_tasks","notes":"property_notes","deadlines":"property_deadlines","sent_offers":"property_sent_offers"}
 IDS={"contacts":"contact_id","tasks":"task_id","notes":"note_id","deadlines":"deadline_id","sent_offers":"sent_offer_id"}
 @classmethod
 def list(cls,kind,property_id):
  order={"contacts":"is_primary","tasks":"due_at","notes":"is_pinned","deadlines":"due_at","sent_offers":"sent_at"}[kind]
  return supabase.table(cls.TABLES[kind]).select("*").eq("property_id",property_id).order(order,desc=kind in ("contacts","notes","sent_offers")).execute().data
 @classmethod
 def get(cls,kind,property_id,entity_id):
  rows=supabase.table(cls.TABLES[kind]).select("*").eq("property_id",property_id).eq(cls.IDS[kind],entity_id).execute().data
  return rows[0] if rows else None
 @classmethod
 def create(cls,kind,property_id,data): return supabase.table(cls.TABLES[kind]).insert({**data,"property_id":property_id}).execute().data[0]
 @classmethod
 def update(cls,kind,property_id,entity_id,data):
  data={**data,"updated_at":datetime.now(timezone.utc).isoformat()}; rows=supabase.table(cls.TABLES[kind]).update(data).eq("property_id",property_id).eq(cls.IDS[kind],entity_id).execute().data
  return rows[0] if rows else None
 @classmethod
 def delete(cls,kind,property_id,entity_id): return supabase.table(cls.TABLES[kind]).delete().eq("property_id",property_id).eq(cls.IDS[kind],entity_id).execute().data
 @classmethod
 def all(cls,kind): return supabase.table(cls.TABLES[kind]).select("*").execute().data
 @staticmethod
 def activity(property_id,activity_type,entity_type,entity_id,title,description=None,metadata=None):
  return supabase.table("property_activity").insert({"property_id":property_id,"activity_type":activity_type,"entity_type":entity_type,"entity_id":entity_id,"title":title,"description":description,"metadata":metadata or {}}).execute().data[0]
 @staticmethod
 def activities(property_id): return supabase.table("property_activity").select("*").eq("property_id",property_id).order("occurred_at",desc=True).execute().data
 @staticmethod
 def history(property_id): return supabase.table("property_workflow_history").select("*").eq("property_id",property_id).order("changed_at",desc=True).execute().data
 @staticmethod
 def add_history(data): return supabase.table("property_workflow_history").insert(data).execute().data[0]
 @staticmethod
 def clear_primary(property_id): supabase.table("property_contacts").update({"is_primary":False}).eq("property_id",property_id).execute()
