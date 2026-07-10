from fastapi import APIRouter

from app.services.property_service import PropertyService
from app.services.opportunity_service import OpportunityService

router = APIRouter(
    prefix="/opportunities",
    tags=["Opportunities"],
)


@router.get("/{property_id}")
async def analyze(property_id: str):

    property_data = PropertyService.get(property_id)

    return OpportunityService.analyze(property_data)