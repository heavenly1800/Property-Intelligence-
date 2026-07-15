import re
from datetime import datetime, timezone
from urllib.parse import unquote, urlsplit, urlunsplit
from uuid import uuid4

from app.infrastructure.database.property_repository import PropertyRepository
from app.infrastructure.database.share_intake_repository import ShareIntakeRepository
from app.services.listing_analysis_service import ListingAnalysisService


class ShareIntakeError(ValueError):
    pass


class ShareIntakeService:
    RESTRICTED_DOMAINS = ("zillow.com", "redfin.com", "realtor.com")
    STREET_PATTERN = re.compile(
        r"\b\d{1,6}\s+[A-Za-z0-9][A-Za-z0-9.'# -]{1,70}\s+"
        r"(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|"
        r"Court|Ct|Circle|Cir|Way|Place|Pl|Parkway|Pkwy|Highway|Hwy|Trail|Trl)\b",
        re.IGNORECASE,
    )

    @classmethod
    def create(cls, data: dict):
        source_url = cls.normalize_url(data.get("source_url"))
        payload = {
            **data,
            "source_url": source_url,
            "source_domain": cls.source_domain(source_url),
            "status": "pending",
        }
        return ShareIntakeRepository.create(payload)

    @classmethod
    def process(cls, share_id: str):
        share = ShareIntakeRepository.get(share_id)
        if not share:
            return None
        if share.get("status") == "completed":
            return share

        ShareIntakeRepository.update(share_id, {"status": "processing", "error_message": None})
        address = cls.extract_address(share)
        listing_text = (share.get("shared_text") or "").strip()
        if not address and not listing_text:
            message = "Share a recognizable street address or paste listing text to process this share."
            ShareIntakeRepository.update(share_id, {"status": "needs_input", "error_message": message})
            raise ShareIntakeError(message)
        if not address:
            message = "No usable street address was found in the explicitly shared content. Add the address and try again."
            ShareIntakeRepository.update(share_id, {"status": "needs_input", "error_message": message})
            raise ShareIntakeError(message)

        normalized_address = cls.normalize_address(address)
        existing = PropertyRepository.find_by_address(normalized_address)
        matched_id = existing.get("property_id") if existing else None
        created_id = None
        property_id = matched_id
        if not property_id:
            created_id = f"PROP-SHARE-{uuid4().hex[:8].upper()}"
            PropertyRepository.create({"property_id": created_id, "address": normalized_address})
            property_id = created_id

        updates = {"listing_url": share.get("source_url"), "listing_source": share.get("source_domain")}
        if listing_text:
            updates.update(ListingAnalysisService.analyze(listing_text))
        PropertyRepository.update(property_id, updates)

        return ShareIntakeRepository.update(share_id, {
            "status": "completed",
            "detected_address": normalized_address,
            "matched_property_id": matched_id,
            "created_property_id": created_id,
            "processed_at": datetime.now(timezone.utc).isoformat(),
            "error_message": None,
        })

    @staticmethod
    def normalize_url(value: str | None):
        if not value or not value.strip():
            return None
        value = value.strip()
        if not re.match(r"^https?://", value, re.IGNORECASE):
            value = f"https://{value}"
        parts = urlsplit(value)
        if parts.scheme.lower() not in ("http", "https") or not parts.hostname:
            raise ShareIntakeError("Enter a valid http or https listing URL.")
        host = parts.hostname.lower()
        if parts.port:
            host = f"{host}:{parts.port}"
        return urlunsplit((parts.scheme.lower(), host, parts.path or "", parts.query, ""))

    @staticmethod
    def source_domain(source_url: str | None):
        if not source_url:
            return None
        domain = (urlsplit(source_url).hostname or "").lower()
        return domain[4:] if domain.startswith("www.") else domain

    @classmethod
    def extract_address(cls, share: dict):
        # Only user-provided text and decoded URL path/query are inspected. No network request is made.
        candidates = [share.get("shared_text"), share.get("title"), share.get("notes")]
        source_url = share.get("source_url")
        if source_url:
            parts = urlsplit(source_url)
            candidates.append(unquote(f"{parts.path} {parts.query}").replace("-", " ").replace("_", " "))
        for candidate in candidates:
            match = cls.STREET_PATTERN.search(candidate or "")
            if match:
                return match.group(0)
        return None

    @staticmethod
    def normalize_address(value: str):
        return re.sub(r"\s+", " ", value).strip(" ,")
