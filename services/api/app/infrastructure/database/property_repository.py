from app.infrastructure.database.supabase import supabase


class PropertyRepository:
    TABLE = "properties"

    @staticmethod
    def get_all():
        return (
            supabase.table(PropertyRepository.TABLE)
            .select("*")
            .execute()
            .data
        )

    @staticmethod
    def get(property_id: str):
        results = (
            supabase.table(PropertyRepository.TABLE)
            .select("*")
            .eq("property_id", property_id)
            .execute()
            .data
        )

        return results[0] if results else None

    @staticmethod
    def create(data: dict):
        result = (
            supabase.table(PropertyRepository.TABLE)
            .insert(data)
            .execute()
        )

        return result.data

    @staticmethod
    def update(property_id: str, data: dict):
        result = (
            supabase.table(PropertyRepository.TABLE)
            .update(data)
            .eq("property_id", property_id)
            .execute()
        )

        return result.data

    @staticmethod
    def find_by_address(address: str):
        results = (
            supabase.table(PropertyRepository.TABLE)
            .select("*")
            .ilike("address", address)
            .limit(1)
            .execute()
            .data
        )
        return results[0] if results else None
