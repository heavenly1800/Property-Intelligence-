from fastapi import APIRouter, HTTPException

from app.infrastructure.database.share_intake_repository import ShareIntakeRepository
from app.schemas.share_intake import ShareIntakeCreate, ShareIntakeResponse
from app.services.share_intake_service import ShareIntakeError, ShareIntakeService

router = APIRouter(prefix="/share-intake", tags=["Share Intake"])


@router.post("", response_model=ShareIntakeResponse, status_code=201)
async def create_share_intake(request: ShareIntakeCreate):
    try:
        return ShareIntakeService.create(request.model_dump())
    except ShareIntakeError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@router.get("/{share_id}", response_model=ShareIntakeResponse)
async def get_share_intake(share_id: str):
    share = ShareIntakeRepository.get(share_id)
    if not share:
        raise HTTPException(status_code=404, detail="Share intake not found.")
    return share


@router.post("/{share_id}/process", response_model=ShareIntakeResponse)
async def process_share_intake(share_id: str):
    try:
        share = ShareIntakeService.process(share_id)
    except ShareIntakeError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    if not share:
        raise HTTPException(status_code=404, detail="Share intake not found.")
    return share
