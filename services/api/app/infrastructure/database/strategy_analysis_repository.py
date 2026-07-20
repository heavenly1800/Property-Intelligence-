from app.infrastructure.database.supabase import supabase


class StrategyAnalysisRepository:
    TABLE = "property_strategy_analysis"
    RESULT_TABLE = "property_strategy_results"

    @classmethod
    def latest(cls, property_id: str):
        rows = supabase.table(cls.TABLE).select("*").eq("property_id", property_id).order("analyzed_at", desc=True).limit(1).execute().data
        if not rows: return None
        analysis = rows[0]
        analysis["results"] = supabase.table(cls.RESULT_TABLE).select("*").eq("strategy_analysis_id", analysis["strategy_analysis_id"]).order("rank").execute().data
        return analysis

    @classmethod
    def create(cls, analysis: dict):
        values = dict(analysis); results = values.pop("results")
        saved = supabase.table(cls.TABLE).insert(values).execute().data[0]
        result_rows = [{**item, "strategy_analysis_id": saved["strategy_analysis_id"]} for item in results]
        saved["results"] = supabase.table(cls.RESULT_TABLE).insert(result_rows).execute().data
        return saved
