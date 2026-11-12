from fastapi import APIRouter, HTTPException

from app.services.property_service import PropertyService
from app.services.opportunity_service import OpportunityService

router = APIRouter(
    prefix="/opportunities",
    tags=["Opportunities"],
)


@router.get("/{property_id}")
async def analyze(property_id: str):

    property_data = PropertyService.get(property_id)

    if property_data is None:
        raise HTTPException(status_code=404, detail="Property not found.")

    return OpportunityService.analyze(property_data)
