from app.infrastructure.database.supabase import supabase


class RepairCostRepository:
    PROFILE_TABLE = "repair_cost_profiles"
    ITEM_TABLE = "repair_cost_items"

    @classmethod
    def list_profiles(cls):
        return supabase.table(cls.PROFILE_TABLE).select("*").order("profile_name").execute().data

    @classmethod
    def get_profile(cls, profile_id: str):
        rows = supabase.table(cls.PROFILE_TABLE).select("*").eq("profile_id", profile_id).execute().data
        return rows[0] if rows else None

    @classmethod
    def create_profile(cls, data: dict):
        return supabase.table(cls.PROFILE_TABLE).insert(data).execute().data[0]

    @classmethod
    def update_profile(cls, profile_id: str, data: dict):
        rows = supabase.table(cls.PROFILE_TABLE).update(data).eq("profile_id", profile_id).execute().data
        return rows[0] if rows else None

    @classmethod
    def delete_profile(cls, profile_id: str):
        return supabase.table(cls.PROFILE_TABLE).delete().eq("profile_id", profile_id).execute().data

    @classmethod
    def list_items(cls, profile_id: str):
        return supabase.table(cls.ITEM_TABLE).select("*").eq("profile_id", profile_id).order("category").execute().data

    @classmethod
    def create_item(cls, profile_id: str, data: dict):
        return supabase.table(cls.ITEM_TABLE).insert({**data, "profile_id": profile_id}).execute().data[0]

    @classmethod
    def update_item(cls, item_id: str, data: dict):
        rows = supabase.table(cls.ITEM_TABLE).update(data).eq("item_id", item_id).execute().data
        return rows[0] if rows else None

    @classmethod
    def delete_item(cls, item_id: str):
        return supabase.table(cls.ITEM_TABLE).delete().eq("item_id", item_id).execute().data
