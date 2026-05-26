from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import get_settings

@asynccontextmanager
async def lifespan(app: FastAPI):
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

@app.get("/api/health")
async def health():
    return {"status": "ok"}
