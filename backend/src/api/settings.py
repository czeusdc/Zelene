"""Module: User settings API endpoints.

This module handles retrieval and persistence of per-company user settings
including API keys and model preferences.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from uuid import UUID
from src.db.connection import get_db
from src.db.models import UserSettings

router = APIRouter(prefix="/api/settings", tags=["settings"])


class SettingsUpdate(BaseModel):
    """Payload for updating user settings for a company."""

    company_id: str
    gemini_api_key: str | None = None
    gemini_model: str | None = None


@router.get("")
async def get_settings(company_id: str, db: AsyncSession = Depends(get_db)):
    """Fetch settings for a given company (API key is masked)."""
    result = await db.execute(select(UserSettings).where(UserSettings.company_id == UUID(company_id)))
    settings = result.scalar_one_or_none()
    if not settings:
        raise HTTPException(status_code=404, detail="Settings not found")
    return {
        "gemini_api_key": "********" if settings.gemini_api_key else None,
        "gemini_model": settings.gemini_model,
        "has_key": bool(settings.gemini_api_key),
    }

@router.post("")
async def save_settings(req: SettingsUpdate, db: AsyncSession = Depends(get_db)):
    """Update the stored settings for a company."""
    result = await db.execute(select(UserSettings).where(UserSettings.company_id == UUID(req.company_id)))
    settings = result.scalar_one_or_none()
    if not settings:
        raise HTTPException(status_code=404, detail="Settings not found")
    if req.gemini_api_key is not None:
        settings.gemini_api_key = req.gemini_api_key
    if req.gemini_model is not None:
        settings.gemini_model = req.gemini_model
    # settings is already tracked by the session (fetched via select)
    await db.commit()
    return {"updated": True}
