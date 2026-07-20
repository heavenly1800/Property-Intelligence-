from fastapi import APIRouter, HTTPException

from app.infrastructure.database.repair_cost_repository import RepairCostRepository
from app.schemas.repair_cost import CostItemInput, CostItemPatch, CostProfileInput, CostProfilePatch


router = APIRouter(prefix="/repair-cost-profiles", tags=["Repair Cost Profiles"])


@router.get("")
async def list_profiles(): return RepairCostRepository.list_profiles()


@router.post("", status_code=201)
async def create_profile(data: CostProfileInput): return RepairCostRepository.create_profile(data.model_dump(mode="json"))


@router.get("/{profile_id}")
async def get_profile(profile_id: str):
    profile = RepairCostRepository.get_profile(profile_id)
    if not profile: raise HTTPException(404, "Repair cost profile was not found.")
    return {**profile, "items": RepairCostRepository.list_items(profile_id)}


@router.patch("/{profile_id}")
async def update_profile(profile_id: str, data: CostProfilePatch):
    result = RepairCostRepository.update_profile(profile_id, data.model_dump(exclude_unset=True, mode="json"))
    if not result: raise HTTPException(404, "Repair cost profile was not found.")
    return result


@router.delete("/{profile_id}", status_code=204)
async def delete_profile(profile_id: str): RepairCostRepository.delete_profile(profile_id)


@router.get("/{profile_id}/items")
async def list_items(profile_id: str): return RepairCostRepository.list_items(profile_id)


@router.post("/{profile_id}/items", status_code=201)
async def create_item(profile_id: str, data: CostItemInput): return RepairCostRepository.create_item(profile_id, data.model_dump(mode="json"))


@router.patch("/{profile_id}/items/{item_id}")
async def update_item(profile_id: str, item_id: str, data: CostItemPatch):
    result = RepairCostRepository.update_item(item_id, data.model_dump(exclude_unset=True, mode="json"))
    if not result: raise HTTPException(404, "Repair cost item was not found.")
    return result


@router.delete("/{profile_id}/items/{item_id}", status_code=204)
async def delete_item(profile_id: str, item_id: str): RepairCostRepository.delete_item(item_id)
