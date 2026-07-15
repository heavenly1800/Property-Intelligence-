from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile

from app.infrastructure.database.property_media_repository import PropertyMediaRepository
from app.infrastructure.database.supabase import supabase


class PropertyMediaService:
    BUCKET = "property-media"
    ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
    MAX_BYTES = 10 * 1024 * 1024

    @classmethod
    async def upload(cls, property_id: str, file: UploadFile):
        content = await file.read()
        if not content or len(content) > cls.MAX_BYTES:
            raise HTTPException(400, "Photo must be between 1 byte and 10 MB.")
        content_type = cls._image_type(content, file.content_type)
        if content_type is None:
            raise HTTPException(400, "Only JPEG, PNG, WebP, and GIF images are supported.")
        media_id = str(uuid4())
        filename = Path(file.filename or "photo").name
        path = f"{property_id}/{media_id}-{filename}"
        supabase.storage.from_(cls.BUCKET).upload(path, content, {"content-type": content_type})
        public_url = supabase.storage.from_(cls.BUCKET).get_public_url(path)
        existing = PropertyMediaRepository.list(property_id)
        return PropertyMediaRepository.create({"media_id": media_id, "property_id": property_id, "storage_path": path, "public_url": public_url, "original_filename": filename, "media_type": content_type, "source_type": "manual_upload", "is_primary": not existing, "sort_order": len(existing), "analysis_status": "pending"})

    @classmethod
    def _image_type(cls, content: bytes, declared_type: str | None) -> str | None:
        signatures = (
            (b"\xff\xd8\xff", "image/jpeg"),
            (b"\x89PNG\r\n\x1a\n", "image/png"),
            (b"GIF87a", "image/gif"),
            (b"GIF89a", "image/gif"),
        )
        for signature, content_type in signatures:
            if content.startswith(signature):
                return content_type
        if content.startswith(b"RIFF") and content[8:12] == b"WEBP":
            return "image/webp"
        return declared_type if declared_type in cls.ALLOWED_TYPES else None

    @classmethod
    def delete(cls, media_id: str):
        media = PropertyMediaRepository.get(media_id)
        if not media: raise HTTPException(404, "Media not found.")
        supabase.storage.from_(cls.BUCKET).remove([media["storage_path"]])
        PropertyMediaRepository.delete(media_id)

    @classmethod
    def set_primary(cls, property_id: str, media_id: str):
        for media in PropertyMediaRepository.list(property_id): PropertyMediaRepository.update(media["media_id"], {"is_primary": media["media_id"] == media_id})
        return PropertyMediaRepository.get(media_id)
