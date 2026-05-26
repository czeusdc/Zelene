"""Module: Application settings and configuration for the Zelene backend.

This module defines the Settings class using pydantic-settings to load
configuration from environment variables and a .env file.
"""

from pydantic import Field
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application-wide configuration loaded from environment and .env file."""

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/zelene"
    gemini_api_key: str | None = None
    bright_data_api_key: str | None = None
    simulation_speed: float = Field(gt=0, default=1.0)
    backend_url: str = "http://localhost:8000"
    mode: str = "auto"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    """Return a cached singleton instance of the application settings."""
    return Settings()
