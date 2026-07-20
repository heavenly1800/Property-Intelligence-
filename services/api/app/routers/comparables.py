from fastapi import APIRouter, HTTPException

from app.infrastructure.database.comparable_repository import ComparableRepository
from app.infrastructure.database.property_repository import PropertyRepository
from app.schemas.comparable import ComparableInput, ComparablePatch
from app.services.comparables.service import ComparableAnalysisService


router = APIRouter(prefix="/properties/{property_id}/comparables", tags=["Property Comparables"])


def require_property(property_id: str):
    subject = PropertyRepository.get(property_id)
    if not subject: raise HTTPException(404, "Property was not found.")
    return subject


@router.get("")
async def list_comparables(property_id: str): require_property(property_id); return ComparableRepository.list(property_id)


@router.post("", status_code=201)
async def create_comparable(property_id: str, data: ComparableInput): require_property(property_id); return ComparableRepository.create(property_id, data.model_dump(mode="json"))


@router.post("/analyze")
async def analyze_comparables(property_id: str):
    subject = require_property(property_id)
    scored, analysis = ComparableAnalysisService.analyze(subject, ComparableRepository.list(property_id))
    ComparableRepository.upsert_many(scored)
    return ComparableRepository.upsert_analysis(analysis)


@router.get("/analysis")
async def get_comparable_analysis(property_id: str):
    require_property(property_id); analysis = ComparableRepository.get_analysis(property_id)
    if not analysis: raise HTTPException(404, "Comparables have not been analyzed for this property.")
    return analysis


@router.patch("/{comparable_id}")
async def update_comparable(property_id: str, comparable_id: str, data: ComparablePatch):
    require_property(property_id); values = data.model_dump(exclude_unset=True, mode="json")
    if values.get("included") is False: values["exclusion_reason"] = "manually excluded"
    elif values.get("included") is True: values["exclusion_reason"] = None
    result = ComparableRepository.update(property_id, comparable_id, values)
    if not result: raise HTTPException(404, "Comparable was not found.")
    return result


@router.delete("/{comparable_id}", status_code=204)
async def delete_comparable(property_id: str, comparable_id: str): require_property(property_id); ComparableRepository.delete(property_id, comparable_id)
