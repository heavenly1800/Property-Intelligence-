from app.infrastructure.database.supabase import supabase


class ShareIntakeRepository:
    TABLE = "share_intake"

    @classmethod
    def create(cls, data: dict):
        result = supabase.table(cls.TABLE).insert(data).execute().data
        return result[0] if result else None

    @classmethod
    def get(cls, share_id: str):
        result = (
            supabase.table(cls.TABLE)
            .select("*")
            .eq("share_id", share_id)
            .execute()
            .data
        )
        return result[0] if result else None

    @classmethod
    def update(cls, share_id: str, data: dict):
        result = (
            supabase.table(cls.TABLE)
            .update(data)
            .eq("share_id", share_id)
            .execute()
            .data
        )
        return result[0] if result else None
