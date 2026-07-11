from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.properties import router as property_router
from app.routers.opportunities import router as opportunity_router
from app.routers.intake import router as intake_router

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