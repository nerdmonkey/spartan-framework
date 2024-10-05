import logging
from functools import lru_cache
from typing import Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings

from dotenv import load_dotenv

# Load the .env file
load_dotenv(dotenv_path=".env")

# Configure the logger
log = logging.getLogger("uvicorn")

class Settings(BaseSettings):
    """
    Configuration class for application settings.
    """
    ALLOWED_ORIGINS: str
    APP_ENVIRONMENT: str
    APP_DEBUG: bool
    DB_TYPE: str
    DB_DRIVER: str
    DB_HOST: str
    DB_PORT: Optional[int] = None
    DB_NAME: str
    DB_USERNAME: str
    DB_PASSWORD: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @field_validator("DB_PORT", mode='before')
    def default_db_port(cls, v):
        try:
            return int(v)
        except (TypeError, ValueError):
            return None

@lru_cache()
def get_settings() -> Settings:
    log.info("Loading config settings from the environment...")
    return Settings()
