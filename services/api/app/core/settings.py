from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


API_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = API_ROOT / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    RENTCAST_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    OPENAI_VISION_MODEL: str = "gpt-5.4-mini"
    OPENAI_VISION_TIMEOUT_SECONDS: float = 60
    PHOTO_ANALYSIS_MAX_BATCH_SIZE: int = 12
    PHOTO_ANALYSIS_CONCURRENCY: int = 3
    PHOTO_REPAIR_COST_ASSUMPTIONS_JSON: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
