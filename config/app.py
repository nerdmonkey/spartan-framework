import logging
from functools import lru_cache

from pydantic import BaseSettings

# Configure the logger
log = logging.getLogger("uvicorn")


class Settings(BaseSettings):
    """
    Configuration settings of the application, loaded from environment variables.

    Attributes:
        ALLOWED_ORIGINS (str): Comma-separated list of allowed origins for CORS.
        APP_ENVIRONMENT (str): The current environment of the app (e.g., development, production).
        DB_TYPE (str): Type of the database (e.g., sqlite, postgres).
        DB_HOST (str): Host address of the database.
        DB_NAME (str): Name of the database.
        DB_USERNAME (str): Username for the database.
        DB_PASSWORD (str): Password for the database.
    """

    ALLOWED_ORIGINS: str
    APP_ENVIRONMENT: str
    DB_TYPE: str
    DB_HOST: str
    DB_NAME: str
    DB_USERNAME: str
    DB_PASSWORD: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """
    Retrieve and cache the application settings.

    Returns:
        Settings: The cached application settings.
    """
    log.info("Loading config settings from the environment...")
    return Settings()
