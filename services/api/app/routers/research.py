from fastapi import APIRouter, HTTPException

from app.services.research.service import ResearchService
from app.services.research.providers.models import ResearchResult

router = APIRouter(
    prefix="/research",
    tags=["Research"],
)


@router.post("/{property_id}/run", response_model=ResearchResult)
async def run_research(property_id: str):
    result = await ResearchService.run(property_id)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Property not found.",
        )

    return result
