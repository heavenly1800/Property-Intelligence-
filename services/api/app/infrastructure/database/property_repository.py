from app.infrastructure.database.supabase import supabase


class PropertyRepository:
    @staticmethod
    def get_all():
        return (
            supabase.table("properties")
            .select("*")
            .execute()
            .data
        )

    @staticmethod
    def get(property_id: str):
        results = (
            supabase.table("properties")
            .select("*")
            .eq("property_id", property_id)
            .execute()
            .data
        )

        return results[0] if results else None

    @staticmethod
    def create(data: dict):
        return (
            supabase.table("properties")
            .insert(data)
            .execute()
            .data
        )