from fastapi import APIRouter, HTTPException
from app.infrastructure.database.financing_repository import FinancingRepository
from app.schemas.financing import FinancingScenarioPatch, FinancingScenarioRequest
from app.services.financing_analysis_orchestrator import FinancingAnalysisOrchestrator

router = APIRouter(prefix="/properties/{property_id}", tags=["Financing"])

@router.post("/financing-scenarios")
async def create_scenario(property_id: str, request: FinancingScenarioRequest):
    return FinancingRepository.create_scenario(property_id, request.model_dump())
@router.get("/financing-scenarios")
async def list_scenarios(property_id: str): return FinancingRepository.list_scenarios(property_id)
@router.patch("/financing-scenarios/{scenario_id}")
async def update_scenario(property_id: str, scenario_id: str, request: FinancingScenarioPatch):
    result = FinancingRepository.update_scenario(property_id, scenario_id, request.model_dump(exclude_unset=True))
    if not result: raise HTTPException(404, "Financing scenario was not found.")
    return result
@router.post("/financing-scenarios/{scenario_id}/analyze")
async def analyze_scenario(property_id: str, scenario_id: str):
    result = FinancingAnalysisOrchestrator.analyze(property_id, scenario_id)
    if not result: raise HTTPException(404, "Property or financing scenario was not found.")
    return result
@router.get("/financing-analysis")
async def latest_analysis(property_id: str):
    result = FinancingRepository.latest_analysis(property_id)
    if not result: raise HTTPException(404, "No saved financing analysis exists for this property.")
    return result
@router.get("/financing-analysis/history")
async def analysis_history(property_id: str): return FinancingRepository.history(property_id)
