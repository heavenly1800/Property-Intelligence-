from fastapi import APIRouter
from pydantic import BaseModel
from app.services.intake_service import IntakeService


router = APIRouter(
    prefix="/intake",
    tags=["Intake"],
)


class IntakeRequest(BaseModel):
    input: str


@router.post("")
async def intake(request: IntakeRequest):

    input_type = IntakeService.detect_input_type(
        request.input
    )

    return {
        "success": True,
        "input": request.input,
        "type": input_type,
    }