import json
import logging
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.auth import auth_middleware
from app.core.deployment import configure_logging, deployment_middleware, http_exception_handler, validation_exception_handler
from app.core.settings import get_settings
from app.infrastructure.database.supabase import service_supabase
from app.routers.auth import router as auth_router
from app.routers.buyers import router as buyers_router
from app.routers.communications import router as communications_router
from app.routers.comparables import router as comparables_router
from app.routers.crm import router as crm_router
from app.routers.decision import router as decision_router
from app.routers.financing import router as financing_router
from app.routers.intake import router as intake_router
from app.routers.media import router as media_router
from app.routers.notifications import router as notifications_router
from app.routers.offer_analysis import router as offer_analysis_router
from app.routers.opportunities import router as opportunity_router
from app.routers.properties import router as property_router
from app.routers.repair_costs import router as repair_costs_router
from app.routers.research import router as research_router
from app.routers.share_intake import router as share_intake_router
from app.routers.strategy_analysis import router as strategy_analysis_router

ROUTERS = [property_router, opportunity_router, intake_router, research_router, decision_router, media_router,
           share_intake_router, repair_costs_router, comparables_router, strategy_analysis_router,
           offer_analysis_router, financing_router, crm_router, notifications_router, communications_router,
           auth_router]

def create_app() -> FastAPI:
    settings = get_settings()
    settings.validate_runtime()
    configure_logging()
    application = FastAPI(
        title="Property Intelligence API",
        version=settings.APP_VERSION,
        description="The backend API for Property Intelligence.",
        docs_url="/docs" if settings.docs_enabled else None,
        redoc_url="/redoc" if settings.docs_enabled else None,
        openapi_url="/openapi.json" if settings.docs_enabled else None,
    )
    application.add_exception_handler(RequestValidationError, validation_exception_handler)
    application.add_exception_handler(HTTPException, http_exception_handler)
    application.add_exception_handler(StarletteHTTPException, http_exception_handler)
    application.middleware("http")(auth_middleware)
    application.middleware("http")(deployment_middleware)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.frontend_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Organization-ID", "X-Request-ID", "Idempotency-Key"],
        expose_headers=["X-Request-ID", "Retry-After"],
    )
    if settings.trusted_hosts:
        application.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.trusted_hosts)

    @application.on_event("startup")
    async def startup_diagnostics():
        logging.getLogger("property_intelligence").info(json.dumps({
            "event": "startup",
            "version": settings.APP_VERSION,
            "build_id": settings.BUILD_ID,
            "environment": settings.APP_ENV,
            "docs_enabled": settings.docs_enabled,
            "configured_origins_count": len(settings.frontend_origins),
            "scanner_mode": settings.SCANNER_MODE,
        }, separators=(",", ":")))

    @application.get("/")
    async def root():
        return {"application": "Property Intelligence", "status": "Running", "version": settings.APP_VERSION}

    @application.get("/health")
    @application.get("/health/live")
    async def health_live():
        return {"status": "live"}

    @application.get("/health/ready")
    async def health_ready():
        from fastapi.responses import JSONResponse
        errors = settings.validation_errors()
        if not errors:
            try:
                service_supabase.table("organizations").select("organization_id").limit(1).execute()
            except Exception:
                errors.append("Supabase connectivity check failed.")
        status = 200 if not errors else 503
        return JSONResponse({"status": "ready" if not errors else "not_ready", "checks": {"configuration": not settings.validation_errors(), "supabase": not errors}, "issues": errors}, status_code=status)

    @application.get("/health/version")
    async def health_version():
        return {"version": settings.APP_VERSION, "environment": settings.APP_ENV, "build_id": settings.BUILD_ID}

    for router in ROUTERS:
        application.include_router(router)
    return application

app = create_app()
