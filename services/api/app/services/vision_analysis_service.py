import asyncio
import base64
from datetime import datetime, timezone

from fastapi import HTTPException
from openai import AsyncOpenAI, APIConnectionError, APITimeoutError, RateLimitError

from app.core.settings import get_settings
from app.infrastructure.database.property_media_analysis_repository import PropertyMediaAnalysisRepository
from app.infrastructure.database.property_media_repository import PropertyMediaRepository
from app.infrastructure.database.property_repository import PropertyRepository
from app.infrastructure.database.supabase import supabase
from app.schemas.photo_analysis import PhotoConditionOutput
from app.services.repair_cost_service import RepairCostService


class VisionAnalysisService:
    PROMPT_VERSION = "property-visible-condition-v1"
    PROMPT = """Analyze only directly visible property condition in this image. Return the required structured result.
Separate directly observed issues from plausible inferences and inspection unknowns. Be conservative.
Never claim certainty about hidden mold, asbestos, lead, foundation condition, internal plumbing,
internal electrical, HVAC internals, roof decking, sewer, or septic condition. Put those in
unknown_inspection_items unless a specific surface symptom is directly visible; describe only that symptom.
Repair items identify category and visible scope only. Never provide or invent dollar amounts.
Allowed repair categories are: interior paint, exterior paint, flooring, drywall, cabinets, countertops,
appliances, bathroom fixtures, windows, exterior doors, interior doors, roofing surface, siding,
landscaping, debris removal, cleaning, electrical visible repairs, plumbing fixture repairs,
HVAC visible service/replacement allowance, and general contingency. Estimate conservative quantity ranges
and quantity units only when visually defensible; otherwise leave quantities unknown. Never imply image quantities are precise.
Mention occlusion, image quality, and lack of physical inspection in limitations."""

    def __init__(self, client: AsyncOpenAI | None = None):
        settings = get_settings()
        self.model = settings.OPENAI_VISION_MODEL
        self.client = client or AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            timeout=settings.OPENAI_VISION_TIMEOUT_SECONDS,
            max_retries=2,
        )

    async def analyze(self, media: dict) -> dict:
        image = await asyncio.to_thread(
            supabase.storage.from_("property-media").download,
            media["storage_path"],
        )
        if not image:
            raise HTTPException(502, "The stored image could not be retrieved from Property Intelligence storage.")
        encoded = base64.b64encode(image).decode("ascii")
        try:
            response = await self.client.responses.parse(
                model=self.model,
                input=[{
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": self.PROMPT},
                        {"type": "input_image", "image_url": f"data:{media['media_type']};base64,{encoded}", "detail": "high"},
                    ],
                }],
                text_format=PhotoConditionOutput,
            )
        except RateLimitError as error:
            raise HTTPException(429, "OpenAI photo analysis is rate limited. Try again shortly.") from error
        except APITimeoutError as error:
            raise HTTPException(504, "OpenAI photo analysis timed out. Try again.") from error
        except APIConnectionError as error:
            raise HTTPException(502, "OpenAI photo analysis is temporarily unavailable.") from error

        parsed = response.output_parsed
        if parsed is None:
            raise HTTPException(502, "OpenAI returned no valid structured photo analysis.")
        return parsed.model_dump()


class PropertyConditionAnalysisService:
    RATINGS = {"unknown": 0, "excellent": 1, "good": 2, "fair": 3, "poor": 4, "severe": 5}
    RENT_READY = {"unknown": 0, "ready": 1, "minor_work": 2, "substantial_work": 3}

    @classmethod
    async def analyze_media(cls, property_id: str, media_id: str, reanalyze: bool = False, analyzer=None):
        settings = get_settings()
        if not settings.OPENAI_API_KEY and analyzer is None:
            raise HTTPException(503, "OPENAI_API_KEY is not configured on the backend.")
        media = PropertyMediaRepository.get(media_id)
        if not media or media.get("property_id") != property_id:
            raise HTTPException(404, "Photo was not found for this property.")
        if not str(media.get("media_type", "")).startswith("image/"):
            raise HTTPException(415, "Only stored image media can be analyzed.")
        existing = PropertyMediaAnalysisRepository.get(media_id)
        if existing and not reanalyze:
            return existing
        claimed = PropertyMediaRepository.begin_analysis(media_id)
        if not claimed:
            raise HTTPException(409, "This photo is already being analyzed.")

        try:
            analysis_provider = analyzer or VisionAnalysisService()
            output = await analysis_provider.analyze(media)
            property_data = PropertyRepository.get(property_id) or {}
            pricing = RepairCostService.price_analysis(output["estimated_repair_items"], property_data)
            now = datetime.now(timezone.utc).isoformat()
            record = PropertyMediaAnalysisRepository.upsert({
                "media_id": media_id,
                **output,
                "estimated_repair_items": pricing["items"],
                "estimated_repair_cost_low": pricing["total_low"],
                "estimated_repair_cost_high": pricing["total_high"],
                "visible_repair_subtotal_low": pricing["visible_repair_subtotal_low"],
                "visible_repair_subtotal_high": pricing["visible_repair_subtotal_high"],
                "contingency_low": pricing["contingency_low"], "contingency_high": pricing["contingency_high"],
                "regional_profile_id": pricing["profile"]["profile_id"],
                "regional_profile_name": pricing["profile"]["profile_name"],
                "profile_match_confidence": pricing["profile_match_confidence"],
                "profile_match_reason": pricing["profile_match_reason"],
                "cost_assumption_effective_date": pricing["cost_assumption_effective_date"],
                "cost_limitations": pricing["cost_limitations"],
                "model_name": analysis_provider.model,
                "analyzed_at": now,
                "prompt_version": VisionAnalysisService.PROMPT_VERSION,
                "cost_assumption_version": RepairCostService.VERSION,
                "raw_analysis": output,
                "review_status": "pending_review",
                "error_message": None,
            })
            PropertyMediaRepository.update(media_id, {"analysis_status": "completed"})
            await cls.aggregate(property_id)
            return record
        except HTTPException as error:
            PropertyMediaRepository.update(media_id, {"analysis_status": "failed"})
            PropertyMediaAnalysisRepository.upsert({
                "media_id": media_id, "model_name": get_settings().OPENAI_VISION_MODEL,
                "prompt_version": VisionAnalysisService.PROMPT_VERSION,
                "cost_assumption_version": RepairCostService.VERSION,
                "review_status": "analysis_failed", "error_message": str(error.detail),
            })
            raise
        except Exception as error:
            PropertyMediaRepository.update(media_id, {"analysis_status": "failed"})
            PropertyMediaAnalysisRepository.upsert({
                "media_id": media_id, "model_name": get_settings().OPENAI_VISION_MODEL,
                "prompt_version": VisionAnalysisService.PROMPT_VERSION,
                "cost_assumption_version": RepairCostService.VERSION,
                "review_status": "analysis_failed", "error_message": "Invalid response or provider/storage failure.",
            })
            raise HTTPException(502, f"Photo analysis failed safely: {error}") from error

    @classmethod
    async def analyze_all(cls, property_id: str, reanalyze: bool = False):
        settings = get_settings()
        media = PropertyMediaRepository.list(property_id)
        if len(media) > settings.PHOTO_ANALYSIS_MAX_BATCH_SIZE:
            raise HTTPException(400, f"Analyze All supports at most {settings.PHOTO_ANALYSIS_MAX_BATCH_SIZE} photos at a time.")
        semaphore = asyncio.Semaphore(max(1, settings.PHOTO_ANALYSIS_CONCURRENCY))

        async def run(item):
            async with semaphore:
                try:
                    result = await cls.analyze_media(property_id, item["media_id"], reanalyze)
                    return {"media_id": item["media_id"], "status": "completed", "analysis": result}
                except HTTPException as error:
                    return {"media_id": item["media_id"], "status": "failed", "error": str(error.detail)}

        results = await asyncio.gather(*(run(item) for item in media))
        summary = await cls.aggregate(property_id)
        return {"results": results, "summary": summary, "completed": sum(r["status"] == "completed" for r in results), "failed": sum(r["status"] == "failed" for r in results)}

    @classmethod
    async def aggregate(cls, property_id: str):
        analyses = [item for item in PropertyMediaAnalysisRepository.list_for_property(property_id) if item.get("analyzed_at")]
        if not analyses:
            return None
        deduped, unknowns, repairs = {}, {}, {}
        for analysis in analyses:
            area = analysis.get("room_or_area") or (analysis.get("property_media") or {}).get("room_category") or "unknown area"
            for issue in analysis.get("observed_issues") or []:
                key = (issue.get("category", "").lower(), area.lower(), issue.get("description", "").lower())
                entry = deduped.setdefault(key, {**issue, "area": area, "supporting_media_ids": []})
                entry["supporting_media_ids"].append(analysis["media_id"])
            for item in analysis.get("unknown_inspection_items") or []:
                key = (item.get("category", "").lower(), item.get("description", "").lower())
                entry = unknowns.setdefault(key, {**item, "supporting_media_ids": []})
                entry["supporting_media_ids"].append(analysis["media_id"])
            for item in analysis.get("estimated_repair_items") or []:
                key = (item.get("category", "").lower(), item.get("area", area).lower(), item.get("description", "").lower())
                entry = repairs.setdefault(key, {**item, "supporting_media_ids": []})
                entry["supporting_media_ids"].append(analysis["media_id"])
        condition = max((item.get("condition_rating", "unknown") for item in analyses), key=lambda value: cls.RATINGS.get(value, 0))
        rent_ready = max((item.get("rent_ready_status", "unknown") for item in analyses), key=lambda value: cls.RENT_READY.get(value, 0))
        major = [item for item in deduped.values() if item.get("severity") in ("major", "severe")]
        subtotal_low = sum(float(item.get("extended_cost_low") or item.get("estimated_cost_low") or 0) for item in repairs.values())
        subtotal_high = sum(float(item.get("extended_cost_high") or item.get("estimated_cost_high") or 0) for item in repairs.values())
        profile = max(analyses, key=lambda item: float(item.get("profile_match_confidence") or 0))
        contingency_rate_low = max((float(item.get("contingency_low") or 0) / float(item.get("visible_repair_subtotal_low") or 1) for item in analyses), default=0)
        contingency_rate_high = max((float(item.get("contingency_high") or 0) / float(item.get("visible_repair_subtotal_high") or 1) for item in analyses), default=0)
        contingency_low, contingency_high = subtotal_low * contingency_rate_low, subtotal_high * contingency_rate_high
        summary = {
            "property_id": property_id,
            "overall_visible_condition": condition,
            "overall_rent_ready_status": rent_ready,
            "visible_repair_scope_summary": "; ".join(sorted(item.get("description", "") for item in repairs.values() if item.get("description"))),
            "visible_repair_items": list(repairs.values()),
            "visible_repair_subtotal_low": subtotal_low, "visible_repair_subtotal_high": subtotal_high,
            "contingency_low": contingency_low, "contingency_high": contingency_high,
            "estimated_visible_repair_cost_low": subtotal_low + contingency_low,
            "estimated_visible_repair_cost_high": subtotal_high + contingency_high,
            "regional_profile_id": profile.get("regional_profile_id"), "regional_profile_name": profile.get("regional_profile_name"),
            "profile_match_confidence": profile.get("profile_match_confidence", 0),
            "profile_match_reason": profile.get("profile_match_reason"),
            "cost_assumption_effective_date": profile.get("cost_assumption_effective_date"),
            "cost_limitations": profile.get("cost_limitations") or RepairCostService.LIMITATIONS,
            "major_observed_issues": major,
            "required_inspection_items": list(unknowns.values()),
            "analyzed_photo_count": len(analyses),
            "analysis_confidence": sum(float(item.get("analysis_confidence") or 0) for item in analyses) / len(analyses),
            "last_analyzed_at": max(item["analyzed_at"] for item in analyses),
            "cost_assumption_version": RepairCostService.VERSION,
            "review_status": "pending_review",
        }
        return PropertyMediaAnalysisRepository.upsert_summary(summary)
