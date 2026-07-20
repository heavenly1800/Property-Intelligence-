from fastapi import APIRouter, HTTPException

from app.infrastructure.database.offer_analysis_repository import OfferAnalysisRepository
from app.schemas.offer_analysis import ManualOfferRequest, OfferCalculationRequest
from app.services.offer_analysis_orchestrator import OfferAnalysisOrchestrator


router = APIRouter(prefix="/properties/{property_id}", tags=["Offer Analysis"])


@router.post("/offer-analysis")
async def calculate_offer(property_id: str, request: OfferCalculationRequest = OfferCalculationRequest()):
    result = OfferAnalysisOrchestrator.calculate(property_id, request.selected_strategy, request.allow_over_asking_offer)
    if not result: raise HTTPException(404, "Property was not found.")
    return result


@router.get("/offer-analysis")
async def get_offer(property_id: str):
    result = OfferAnalysisRepository.latest(property_id)
    if not result: raise HTTPException(404, "No saved offer analysis exists for this property.")
    return result


@router.post("/offer-analysis/recalculate")
async def recalculate_offer(property_id: str, request: OfferCalculationRequest = OfferCalculationRequest()):
    result = OfferAnalysisOrchestrator.calculate(property_id, request.selected_strategy, request.allow_over_asking_offer)
    if not result: raise HTTPException(404, "Property was not found.")
    return result


@router.post("/offer-analysis/manual")
async def save_manual_offer(property_id: str, request: ManualOfferRequest):
    result = OfferAnalysisOrchestrator.manual(property_id, request.target_offer, request.target_margin, request.notes)
    if not result: raise HTTPException(404, "Property was not found.")
    return result


@router.get("/offer-history")
async def offer_history(property_id: str): return OfferAnalysisRepository.history(property_id)
