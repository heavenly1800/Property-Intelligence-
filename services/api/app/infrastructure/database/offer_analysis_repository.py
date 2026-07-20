from app.infrastructure.database.supabase import supabase


class OfferAnalysisRepository:
    TABLE = "property_offer_analysis"

    @classmethod
    def latest(cls, property_id: str):
        rows = supabase.table(cls.TABLE).select("*").eq("property_id", property_id).order("created_at", desc=True).limit(1).execute().data
        return rows[0] if rows else None

    @classmethod
    def history(cls, property_id: str):
        return supabase.table(cls.TABLE).select("*").eq("property_id", property_id).order("created_at", desc=True).execute().data

    @classmethod
    def create(cls, data: dict):
        return supabase.table(cls.TABLE).insert(data).execute().data[0]
