"""Module: FastAPI application entry point for the Zelene intelligence platform.

This module creates the FastAPI application, configures CORS middleware, and
registers all API routers (company, settings, intelligence, conversation).
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager that eagerly loads settings on startup."""
    get_settings()
    yield

app = FastAPI(title="Zelene", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from src.api.company import router as company_router
app.include_router(company_router)

from src.api.settings import router as settings_router
app.include_router(settings_router)

from src.api.intelligence import router as intelligence_router
app.include_router(intelligence_router)

from src.api.conversation import router as conversation_router
app.include_router(conversation_router)

from src.api.briefing import router as briefing_router
app.include_router(briefing_router)

@app.get("/api/health")
async def health():
    """Health-check endpoint for monitoring and load-balancer probes."""
    return {"status": "ok"}
