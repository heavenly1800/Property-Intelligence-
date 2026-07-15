from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.buyers import router as buyers_router
from app.routers.properties import router as property_router
from app.routers.opportunities import router as opportunity_router
from app.routers.intake import router as intake_router
from app.routers.research import router as research_router
from app.routers.decision import router as decision_router
from app.routers.media import router as media_router
from app.routers.share_intake import router as share_intake_router
from app.infrastructure.database.property_repository import PropertyRepository



app = FastAPI(
    title="Property Intelligence API",
    version="0.1.0",
    description="The backend API for Property Intelligence.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "application": "Property Intelligence",
        "status": "Running",
        "version": "0.1.0",
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
    }




app.include_router(property_router)
app.include_router(opportunity_router)
app.include_router(intake_router)
app.include_router(research_router)
app.include_router(decision_router)
app.include_router(media_router)
app.include_router(share_intake_router)
