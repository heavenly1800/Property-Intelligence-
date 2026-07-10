from fastapi import APIRouter

from app.schemas.property import PropertyResponse
from app.services.property_service import PropertyService

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
