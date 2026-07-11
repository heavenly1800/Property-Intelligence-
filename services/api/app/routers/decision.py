from fastapi import APIRouter, HTTPException

from app.services.decision_service import DecisionService

router = APIRouter(
    prefix="/decision",
    tags=["Decision Engine"],
)


@router.get("/{property_id}")
async def evaluate_property(property_id: str):
    result = DecisionService.evaluate(property_id)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Property not found.",
        )

    return {
        "score": result.score,
        "confidence": result.confidence,
        "reasons": result.reasons,
        "risks": result.risks,
        "next_action": result.next_action,
    }