from fastapi import APIRouter, HTTPException

from app.services.buyer_service import BuyerService

router = APIRouter(
    prefix="/buyers",
    tags=["Buyers"],
)


@router.get("/{property_id}")
async def get_buyers(property_id: str):
    result = BuyerService.find_buyers(property_id)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Property not found.",
        )

    return {
        "buyers": [
            {
                "buyer_name": buyer.buyer_name,
                "purchase_count": buyer.purchase_count,
                "confidence": buyer.confidence,
                "reasons": buyer.reasons,
            }
            for buyer in result.buyers
        ]
    }