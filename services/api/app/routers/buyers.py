from fastapi import APIRouter, HTTPException

from app.core.auth import require_permission
from app.services.buyer.models import BuyerMatchResult
from app.services.buyer_service import BuyerService

router = APIRouter(
    prefix="/buyers",
    tags=["Buyers"],
)


@router.get("/{property_id}", response_model=BuyerMatchResult)
async def get_buyers(property_id: str):
    require_permission("analysis.read")
    result = BuyerService().find_buyers(property_id)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Property not found.",
        )

    return result
