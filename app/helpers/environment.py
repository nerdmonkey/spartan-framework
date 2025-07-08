from functools import lru_cache
from typing import Optional

from dotenv import load_dotenv
from pydantic import ConfigDict, field_validator
from pydantic_settings import BaseSettings

load_dotenv(dotenv_path=".env")


class EnvironmentVariables(BaseSettings):
    """
    EnvironmentVariables is a configuration class for managing application environment variables.
    Attributes:
        APP_NAME (str): The name of the application.
        APP_ENVIRONMENT (str): The current environment (e.g., development, production).
        APP_DEBUG (bool): Flag to enable or disable debug mode.
        APP_MAINTENANCE (bool): Flag to enable or disable maintenance mode. Defaults to False.
        ALLOWED_ORIGINS (str): Comma-separated list of allowed CORS origins.
        LOG_LEVEL (str): Logging level (e.g., INFO, DEBUG).
        LOG_CHANNEL (str): Logging channel to use.
        LOG_DIR (str): Directory where logs are stored.
        DB_TYPE (str): Type of the database (e.g., postgres, mysql).
        DB_DRIVER (str): Database driver to use.
        DB_HOST (str): Database host address.
        DB_PORT (Optional[int]): Database port number. Defaults to None if not provided.
        DB_NAME (str): Name of the database.
        DB_USERNAME (str): Username for database authentication.
        DB_PASSWORD (str): Password for database authentication.
        DB_SSL_CA (Optional[str]): Path to the SSL CA certificate for the database. Defaults to None.
        DB_SSL_VERIFY_CERT (Optional[bool]): Whether to verify the database SSL certificate. Defaults to None.
    Config:
        model_config: Specifies the .env file and encoding to load environment variables.
    Validators:
        default_db_port: Ensures DB_PORT is converted to an integer if possible, otherwise returns None.
    """

    APP_NAME: str
    APP_ENVIRONMENT: str
    APP_DEBUG: bool
    APP_MAINTENANCE: bool = False
    ALLOWED_ORIGINS: str
    LOG_LEVEL: str
    LOG_CHANNEL: str
    LOG_DIR: str
    DB_TYPE: str
    DB_DRIVER: str
    DB_HOST: str
    DB_PORT: Optional[int] = None
    DB_NAME: str
    DB_USERNAME: str
    DB_PASSWORD: str
    DB_SSL_CA: Optional[str] = None
    DB_SSL_VERIFY_CERT: Optional[bool] = None

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")

    @field_validator("DB_PORT", mode="before")
    def default_db_port(cls, v):
        try:
            return int(v)
        except (TypeError, ValueError):
            return None


@lru_cache()
def env(
    var_name: Optional[str] = None, default: Optional[str] = None
) -> Optional[str]:
    """
    Create and return an instance of EnvironmentVariables or a specific environment variable.

    This function initializes and returns an EnvironmentVariables object,
    which is used to manage and access environment variables for the application.
    If a variable name is provided, it returns the value of that specific environment variable.
    If the variable is not found, it returns the provided default value.

    Args:
        var_name (Optional[str]): The name of the environment variable to retrieve.
        default (Optional[str]): The default value to return if the variable is not found.
        Defaults to None.

    Returns:
        EnvironmentVariables or Optional[str]: An instance of the EnvironmentVariables
        class or the value of the specified environment variable, or the default value if not found.
    """
    env_vars = EnvironmentVariables()
    if var_name:
        return getattr(env_vars, var_name, default)
    return env_vars
