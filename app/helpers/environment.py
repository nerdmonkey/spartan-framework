from functools import lru_cache
from typing import Optional

from dotenv import load_dotenv
from pydantic import ConfigDict, field_validator
from pydantic_settings import BaseSettings

load_dotenv(dotenv_path=".env")


class EnvironmentVariables(BaseSettings):
    """
    EnvironmentVariables is a configuration class that loads environment variables
    for the application using Pydantic's BaseSettings. It includes settings for
    application name, environment, debug mode, allowed origins, logging, and database
    connection details.

    Attributes:
        APP_NAME (str): The name of the application.
        APP_ENVIRONMENT (str): The environment in which the application is running
        (e.g., development, production).
        APP_DEBUG (bool): Flag to enable or disable debug mode.
        ALLOWED_ORIGINS (str): Comma-separated list of allowed origins for CORS.
        LOG_LEVEL (str): The logging level (e.g., DEBUG, INFO, WARNING, ERROR).
        LOG_CHANNEL (str): The logging channel to use.
        LOG_FILE (str): The file path for logging output.
        DB_TYPE (str): The type of the database (e.g., PostgreSQL, MySQL).
        DB_DRIVER (str): The database driver to use.
        DB_HOST (str): The hostname of the database server.
        DB_PORT (Optional[int]): The port number of the database server. Defaults to None.
        DB_NAME (str): The name of the database.
        DB_USERNAME (str): The username for the database connection.
        DB_PASSWORD (str): The password for the database connection.
        DB_SSL_CA (Optional[str]): The SSL CA certificate for the database connection.
        Defaults to None.
        DB_SSL_VERIFY_CERT (Optional[bool]): Flag to enable or disable SSL certificate
        verification. Defaults to None.

    Methods:
        default_db_port(cls, v): Validates and converts the database port to an integer.
                                 Returns None if the value is invalid.
    """

    APP_NAME: str
    APP_ENVIRONMENT: str
    APP_DEBUG: bool
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
