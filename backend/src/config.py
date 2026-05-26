from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/zelene"
    gemini_api_key: str | None = None
    bright_data_api_key: str | None = None
    simulation_speed: float = 1.0
    backend_url: str = "http://localhost:8000"
    mode: str = "auto"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

@lru_cache
def get_settings() -> Settings:
    return Settings()
