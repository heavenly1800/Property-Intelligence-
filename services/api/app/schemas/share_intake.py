from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class ShareIntakeCreate(BaseModel):
    source_url: Optional[str] = None
    shared_text: Optional[str] = None
    title: Optional[str] = None
    notes: Optional[str] = None


class ShareIntakeResponse(ShareIntakeCreate):
    share_id: UUID
    source_domain: Optional[str] = None
    status: str
    detected_address: Optional[str] = None
    matched_property_id: Optional[str] = None
    created_property_id: Optional[str] = None
    created_at: datetime
    processed_at: Optional[datetime] = None
    error_message: Optional[str] = None
