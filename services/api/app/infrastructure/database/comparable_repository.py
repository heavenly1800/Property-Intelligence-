from app.infrastructure.database.supabase import supabase


class ComparableRepository:
    TABLE = "property_comparables"
    ANALYSIS_TABLE = "property_comparable_analysis"

    @classmethod
    def list(cls, property_id: str):
        return supabase.table(cls.TABLE).select("*").eq("subject_property_id", property_id).order("created_at").execute().data

    @classmethod
    def get(cls, property_id: str, comparable_id: str):
        rows = supabase.table(cls.TABLE).select("*").eq("subject_property_id", property_id).eq("comparable_id", comparable_id).execute().data
        return rows[0] if rows else None

    @classmethod
    def create(cls, property_id: str, data: dict):
        return supabase.table(cls.TABLE).insert({**data, "subject_property_id": property_id}).execute().data[0]

    @classmethod
    def update(cls, property_id: str, comparable_id: str, data: dict):
        rows = supabase.table(cls.TABLE).update(data).eq("subject_property_id", property_id).eq("comparable_id", comparable_id).execute().data
        return rows[0] if rows else None

    @classmethod
    def delete(cls, property_id: str, comparable_id: str):
        return supabase.table(cls.TABLE).delete().eq("subject_property_id", property_id).eq("comparable_id", comparable_id).execute().data

    @classmethod
    def upsert_many(cls, rows: list[dict]):
        return supabase.table(cls.TABLE).upsert(rows, on_conflict="comparable_id").execute().data if rows else []

    @classmethod
    def get_analysis(cls, property_id: str):
        rows = supabase.table(cls.ANALYSIS_TABLE).select("*").eq("property_id", property_id).execute().data
        return rows[0] if rows else None

    @classmethod
    def upsert_analysis(cls, data: dict):
        return supabase.table(cls.ANALYSIS_TABLE).upsert(data, on_conflict="property_id").execute().data[0]
