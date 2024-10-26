import logging
from functools import lru_cache
from typing import Optional

from dotenv import load_dotenv
from pydantic import ConfigDict, field_validator
from pydantic_settings import BaseSettings

load_dotenv(dotenv_path=".env")

log = logging.getLogger("uvicorn")


class Settings(BaseSettings):
    """
    Configuration class for application settings.
    """

    APP_NAME: str
    APP_ENVIRONMENT: str
    APP_DEBUG: bool
    ALLOWED_ORIGINS: str
    LOG_LEVEL: str
    LOG_FILE: str
    DB_TYPE: str
    DB_DRIVER: str
    DB_HOST: str
    DB_PORT: Optional[int] = None
    DB_NAME: str
    DB_USERNAME: str
    DB_PASSWORD: str
    AWS_REGION: str

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")

    @field_validator("DB_PORT", mode="before")
    def default_db_port(cls, v):
        try:
            return int(v)
        except (TypeError, ValueError):
            return None


@lru_cache()
def get_settings() -> Settings:
    log.info("Loading config settings from the environment...")
    return Settings()
