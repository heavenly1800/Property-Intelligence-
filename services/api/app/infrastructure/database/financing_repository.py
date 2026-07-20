from datetime import datetime, timezone
from app.infrastructure.database.supabase import supabase

class FinancingRepository:
    SCENARIOS = "property_financing_scenarios"
    ANALYSES = "property_financing_analysis"

    @classmethod
    def list_scenarios(cls, property_id):
        return supabase.table(cls.SCENARIOS).select("*").eq("property_id", property_id).order("updated_at", desc=True).execute().data
    @classmethod
    def get_scenario(cls, property_id, scenario_id):
        rows = supabase.table(cls.SCENARIOS).select("*").eq("property_id", property_id).eq("financing_scenario_id", scenario_id).execute().data
        return rows[0] if rows else None
    @classmethod
    def create_scenario(cls, property_id, data):
        if data.get("is_approved"):
            supabase.table(cls.SCENARIOS).update({"is_approved": False}).eq("property_id", property_id).execute()
        return supabase.table(cls.SCENARIOS).insert({**data, "property_id": property_id}).execute().data[0]
    @classmethod
    def update_scenario(cls, property_id, scenario_id, data):
        if data.get("is_approved"):
            supabase.table(cls.SCENARIOS).update({"is_approved": False}).eq("property_id", property_id).execute()
        data["updated_at"] = datetime.now(timezone.utc).isoformat()
        rows = supabase.table(cls.SCENARIOS).update(data).eq("property_id", property_id).eq("financing_scenario_id", scenario_id).execute().data
        return rows[0] if rows else None
    @classmethod
    def create_analysis(cls, data):
        return supabase.table(cls.ANALYSES).insert(data).execute().data[0]
    @classmethod
    def latest_analysis(cls, property_id):
        rows = supabase.table(cls.ANALYSES).select("*").eq("property_id", property_id).order("created_at", desc=True).limit(1).execute().data
        return rows[0] if rows else None
    @classmethod
    def history(cls, property_id):
        return supabase.table(cls.ANALYSES).select("*").eq("property_id", property_id).order("created_at", desc=True).execute().data
