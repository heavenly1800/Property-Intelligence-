from fastapi import APIRouter

from app.schemas.property import PropertyFinancialUpdate, PropertyResponse
from app.services.property_service import PropertyService
from app.services.listing_analysis_service import ListingAnalysisService
from app.infrastructure.database.property_repository import PropertyRepository
from pydantic import BaseModel

router = APIRouter(
    prefix="/properties",
    tags=["Properties"],
)


@router.get("/", response_model=list[PropertyResponse])
async def get_properties():
    return PropertyService.get_all()


@router.get("/{property_id}", response_model=PropertyResponse)
async def get_property(property_id: str):
    return PropertyService.get(property_id)


@router.post("/")
async def create_property(property: PropertyResponse):
    return PropertyService.create(property.model_dump())


@router.put("/{property_id}/financials", response_model=PropertyResponse)
async def update_financials(property_id: str, property: PropertyFinancialUpdate):
    return PropertyService.update_financials(
        property_id,
        property.model_dump(exclude_unset=True),
    )


class ListingText(BaseModel):
    listing_raw_text: str


@router.post("/{property_id}/listing-analysis", response_model=PropertyResponse)
async def analyze_listing(property_id: str, listing: ListingText):
    analysis = ListingAnalysisService.analyze(listing.listing_raw_text)
    PropertyRepository.update(property_id, analysis)
    return PropertyRepository.get(property_id)
