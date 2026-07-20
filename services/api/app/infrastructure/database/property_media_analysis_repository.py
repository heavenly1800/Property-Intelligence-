from app.infrastructure.database.supabase import supabase


class PropertyMediaAnalysisRepository:
    TABLE = "property_media_analysis"
    SUMMARY_TABLE = "property_condition_analysis"

    @classmethod
    def get(cls, media_id: str):
        rows = supabase.table(cls.TABLE).select("*").eq("media_id", media_id).execute().data
        return rows[0] if rows else None

    @classmethod
    def list_for_property(cls, property_id: str):
        return (
            supabase.table(cls.TABLE)
            .select("*, property_media!inner(property_id, room_category)")
            .eq("property_media.property_id", property_id)
            .execute()
            .data
        )

    @classmethod
    def upsert(cls, data: dict):
        return supabase.table(cls.TABLE).upsert(data, on_conflict="media_id").execute().data[0]

    @classmethod
    def get_summary(cls, property_id: str):
        rows = supabase.table(cls.SUMMARY_TABLE).select("*").eq("property_id", property_id).execute().data
        return rows[0] if rows else None

    @classmethod
    def upsert_summary(cls, data: dict):
        return supabase.table(cls.SUMMARY_TABLE).upsert(data, on_conflict="property_id").execute().data[0]
