from fastapi import APIRouter, HTTPException

from app.services.research.service import ResearchService

router = APIRouter(
    prefix="/research",
    tags=["Research"],
)


@router.post("/{property_id}/run")
async def run_research(property_id: str):
    property = await ResearchService.run(property_id)

    if property is None:
        raise HTTPException(
            status_code=404,
            detail="Property not found.",
        )

    return property