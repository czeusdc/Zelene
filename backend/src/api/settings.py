"""Module: User settings API endpoints.

This module handles retrieval and persistence of per-company user settings
including model preferences. API keys are NEVER stored — they come from .env.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from uuid import UUID
from src.db.connection import get_db
from src.db.models import UserSettings
from src.config import get_settings as get_env_settings

router = APIRouter(prefix="/api/settings", tags=["settings"])


class SettingsUpdate(BaseModel):
    """Payload for updating user settings (model only — no API keys)."""

    company_id: str
    gemini_model: str | None = None


@router.get("")
async def get_settings(company_id: str, db: AsyncSession = Depends(get_db)):
    """Fetch settings for a company and check if an API key is configured."""
    try:
        uid = UUID(company_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid company ID format")

    result = await db.execute(
        select(UserSettings).where(UserSettings.company_id == uid)
    )
    settings = result.scalar_one_or_none()
    if not settings:
        raise HTTPException(status_code=404, detail="Settings not found")

    env_settings = get_env_settings()
    return {
        "gemini_model": settings.gemini_model,
        "has_api_key": bool(env_settings.gemini_api_key),
    }


@router.post("")
async def save_settings(req: SettingsUpdate, db: AsyncSession = Depends(get_db)):
    """Update the stored model preference for a company."""
    try:
        uid = UUID(req.company_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid company ID format")

    result = await db.execute(
        select(UserSettings).where(UserSettings.company_id == uid)
    )
    settings = result.scalar_one_or_none()
    if not settings:
        raise HTTPException(status_code=404, detail="Settings not found")

    if req.gemini_model is not None:
        settings.gemini_model = req.gemini_model
    await db.commit()
    return {"updated": True}
