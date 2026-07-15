from app.infrastructure.database.supabase import supabase


class PropertyMediaRepository:
    TABLE = "property_media"

    @classmethod
    def list(cls, property_id: str):
        return supabase.table(cls.TABLE).select("*").eq("property_id", property_id).order("sort_order").execute().data

    @classmethod
    def create(cls, data: dict):
        return supabase.table(cls.TABLE).insert(data).execute().data[0]

    @classmethod
    def update(cls, media_id: str, data: dict):
        return supabase.table(cls.TABLE).update(data).eq("media_id", media_id).execute().data[0]

    @classmethod
    def get(cls, media_id: str):
        rows = supabase.table(cls.TABLE).select("*").eq("media_id", media_id).execute().data
        return rows[0] if rows else None

    @classmethod
    def delete(cls, media_id: str):
        return supabase.table(cls.TABLE).delete().eq("media_id", media_id).execute().data
