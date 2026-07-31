import json
import logging
import re
import time
import uuid
from datetime import datetime, timezone
from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.core.settings import get_settings

logger = logging.getLogger("property_intelligence")
SAFE_REQUEST_ID = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")

def configure_logging() -> None:
    settings = get_settings()
    logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO), format="%(message)s")

def request_id(request: Request) -> str:
    incoming = request.headers.get("X-Request-ID", "")
    return incoming if SAFE_REQUEST_ID.fullmatch(incoming) else str(uuid.uuid4())

def error_body(request: Request, status: int, code: str, message: str, details=None) -> dict:
    body = {"request_id": getattr(request.state, "request_id", request_id(request)), "status": status, "code": code, "message": message}
    if details is not None:
        body["details"] = details
    return body

async def deployment_middleware(request: Request, call_next):
    started = time.perf_counter()
    request.state.request_id = request_id(request)
    try:
        response = await call_next(request)
    except Exception as exc:
        logger.exception("Unhandled request exception", extra={"exception_category": type(exc).__name__})
        response = JSONResponse(error_body(request, 500, "internal_error", "An unexpected error occurred."), status_code=500)
    response.headers["X-Request-ID"] = request.state.request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    if request.url.path not in {"/", "/health", "/health/live", "/health/ready", "/health/version"}:
        response.headers["Cache-Control"] = "no-store"
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "level": "INFO",
        "request_id": request.state.request_id,
        "method": request.method,
        "path": request.url.path,
        "status_code": response.status_code,
        "duration_ms": round((time.perf_counter() - started) * 1000, 2),
        "user_id": getattr(request.state, "user_id", None),
        "organization_id": getattr(request.state, "organization_id", None),
    }
    logger.info(json.dumps(record, separators=(",", ":")))
    return response

async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(error_body(request, exc.status_code, "http_error", str(exc.detail)), status_code=exc.status_code, headers=exc.headers)

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    details = [{"loc": list(item["loc"]), "type": item["type"], "message": item["msg"]} for item in exc.errors()]
    return JSONResponse(error_body(request, 422, "validation_error", "Request validation failed.", details), status_code=422)
