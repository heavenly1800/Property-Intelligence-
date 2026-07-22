from datetime import datetime,timezone
from app.infrastructure.database.supabase import supabase

class NotificationRepository:
 TABLE="property_notifications"
 @classmethod
 def list(cls,filters=None):
  query=supabase.table(cls.TABLE).select("*");filters=filters or {}
  if filters.get("unread_only"):query=query.eq("status","unread")
  for key in ("severity","notification_type","property_id","status"):
   if filters.get(key):query=query.eq(key,filters[key])
  if filters.get("include_dismissed") is False:query=query.neq("status","dismissed")
  if filters.get("due_from"):query=query.gte("scheduled_for",filters["due_from"])
  if filters.get("due_to"):query=query.lte("scheduled_for",filters["due_to"])
  return query.order("triggered_at",desc=True).execute().data
 @classmethod
 def property_records(cls,property_id):return supabase.table(cls.TABLE).select("*").eq("property_id",property_id).execute().data
 @classmethod
 def create(cls,data):return supabase.table(cls.TABLE).insert(data).execute().data[0]
 @classmethod
 def update(cls,notification_id,data):
  rows=supabase.table(cls.TABLE).update({**data,"updated_at":datetime.now(timezone.utc).isoformat()}).eq("notification_id",notification_id).execute().data
  return rows[0] if rows else None
 @classmethod
 def unread_count(cls):return len(supabase.table(cls.TABLE).select("notification_id").eq("status","unread").execute().data)
