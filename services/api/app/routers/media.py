from fastapi import APIRouter, File, UploadFile
from pydantic import BaseModel
from app.infrastructure.database.property_media_repository import PropertyMediaRepository
from app.services.property_media_service import PropertyMediaService

router = APIRouter(prefix="/properties/{property_id}/media", tags=["Property Media"])
class MediaUpdate(BaseModel): caption: str | None = None; room_category: str | None = None; source_url: str | None = None; sort_order: int | None = None
@router.get("")
async def list_media(property_id: str): return PropertyMediaRepository.list(property_id)
@router.post("")
async def upload_media(property_id: str, file: UploadFile = File(...)): return await PropertyMediaService.upload(property_id, file)
@router.patch("/{media_id}")
async def update_media(property_id: str, media_id: str, data: MediaUpdate): return PropertyMediaRepository.update(media_id, data.model_dump(exclude_unset=True))
@router.delete("/{media_id}", status_code=204)
async def delete_media(property_id: str, media_id: str): PropertyMediaService.delete(media_id)
@router.post("/{media_id}/primary")
async def primary_media(property_id: str, media_id: str): return PropertyMediaService.set_primary(property_id, media_id)
