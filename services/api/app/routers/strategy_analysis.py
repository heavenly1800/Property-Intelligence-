from fastapi import APIRouter, HTTPException

from app.infrastructure.database.strategy_analysis_repository import StrategyAnalysisRepository
from app.services.strategy_analysis_orchestrator import StrategyAnalysisOrchestrator


router = APIRouter(prefix="/properties/{property_id}/strategy-analysis", tags=["Deal Strategy Analysis"])


@router.post("")
async def create_strategy_analysis(property_id: str):
    result = StrategyAnalysisOrchestrator.create_once(property_id)
    if not result: raise HTTPException(404, "Property was not found.")
    return result


@router.get("")
async def get_strategy_analysis(property_id: str):
    result = StrategyAnalysisRepository.latest(property_id)
    if not result: raise HTTPException(404, "Deal strategy has not been analyzed for this property.")
    return result


@router.post("/recalculate")
async def recalculate_strategy_analysis(property_id: str):
    result = StrategyAnalysisOrchestrator.calculate(property_id)
    if not result: raise HTTPException(404, "Property was not found.")
    return result
