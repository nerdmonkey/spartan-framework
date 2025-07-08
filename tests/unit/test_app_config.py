import os
from unittest.mock import patch, MagicMock

from app.helpers.environment import EnvironmentVariables, env


def test_settings_loads_env_vars():
    """
    Test that the EnvironmentVariables class correctly loads configuration from environment variables.

    This test sets environment variables and then creates an EnvironmentVariables instance to
    verify that the environment variables are correctly loaded and assigned.
    """
    # Set required environment variables
    test_env_vars = {
        "APP_NAME": "test-app",
        "ALLOWED_ORIGINS": "http://localhost.lan",
        "APP_ENVIRONMENT": "test",
        "APP_DEBUG": "true",
        "LOG_LEVEL": "DEBUG",
        "LOG_CHANNEL": "file",
        "LOG_DIR": "/tmp/logs",
        "DB_TYPE": "sqlite",
        "DB_DRIVER": "sqlite",
        "DB_HOST": "localhost",
        "DB_NAME": "testdb",
        "DB_USERNAME": "user",
        "DB_PASSWORD": "password"
    }

    # Apply environment variables
    for key, value in test_env_vars.items():
        os.environ[key] = value

    try:
        settings = EnvironmentVariables()

        assert settings.APP_NAME == "test-app"
        assert settings.ALLOWED_ORIGINS == "http://localhost.lan"
        assert settings.APP_ENVIRONMENT == "test"
        assert settings.APP_DEBUG is True
        assert settings.LOG_LEVEL == "DEBUG"
        assert settings.LOG_CHANNEL == "file"
        assert settings.LOG_DIR == "/tmp/logs"
        assert settings.DB_TYPE == "sqlite"
        assert settings.DB_DRIVER == "sqlite"
        assert settings.DB_HOST == "localhost"
        assert settings.DB_NAME == "testdb"
        assert settings.DB_USERNAME == "user"
        assert settings.DB_PASSWORD == "password"
        assert settings.APP_MAINTENANCE is False  # Default value
        assert settings.DB_PORT is None  # Default value
        assert settings.DB_SSL_CA is None  # Default value
        assert settings.DB_SSL_VERIFY_CERT is None  # Default value
    finally:
        # Clean up environment variables
        for key in test_env_vars.keys():
            os.environ.pop(key, None)


def test_get_settings_cached():
    """
    Test that the env function uses @lru_cache for returning EnvironmentVariables.

    This test verifies that when env() is called multiple times, it returns
    the same instance of EnvironmentVariables, indicating that the function's result is being cached.
    """
    # Clear the cache first
    env.cache_clear()

    # Set minimal required environment variables
    test_env_vars = {
        "APP_NAME": "test-app",
        "ALLOWED_ORIGINS": "http://localhost",
        "APP_ENVIRONMENT": "test",
        "APP_DEBUG": "false",
        "LOG_LEVEL": "INFO",
        "LOG_CHANNEL": "stream",
        "LOG_DIR": "/tmp",
        "DB_TYPE": "sqlite",
        "DB_DRIVER": "sqlite",
        "DB_HOST": "localhost",
        "DB_NAME": "test.db",
        "DB_USERNAME": "test",
        "DB_PASSWORD": "test"
    }

    for key, value in test_env_vars.items():
        os.environ[key] = value

    try:
        first_call = env()
        second_call = env()

        # Should return the same cached instance
        assert first_call is second_call

        # Verify it's actually an EnvironmentVariables instance
        assert isinstance(first_call, EnvironmentVariables)
    finally:
        # Clean up
        for key in test_env_vars.keys():
            os.environ.pop(key, None)
        env.cache_clear()


def test_env_function_with_variable_name():
    """
    Test that the env function returns specific environment variable values when var_name is provided.
    """
    test_env_vars = {
        "APP_NAME": "test-app",
        "ALLOWED_ORIGINS": "http://localhost",
        "APP_ENVIRONMENT": "test",
        "APP_DEBUG": "false",
        "LOG_LEVEL": "INFO",
        "LOG_CHANNEL": "stream",
        "LOG_DIR": "/tmp",
        "DB_TYPE": "sqlite",
        "DB_DRIVER": "sqlite",
        "DB_HOST": "localhost",
        "DB_NAME": "test.db",
        "DB_USERNAME": "test",
        "DB_PASSWORD": "test"
    }

    for key, value in test_env_vars.items():
        os.environ[key] = value

    try:
        # Test getting specific variables
        assert env("APP_NAME") == "test-app"
        assert env("APP_ENVIRONMENT") == "test"
        assert env("DB_TYPE") == "sqlite"

        # Test getting non-existent variable with default
        assert env("NON_EXISTENT_VAR", "default_value") == "default_value"

        # Test getting non-existent variable without default
        assert env("NON_EXISTENT_VAR") is None
    finally:
        # Clean up
        for key in test_env_vars.keys():
            os.environ.pop(key, None)
        env.cache_clear()


def test_db_port_validator():
    """
    Test that the DB_PORT validator correctly converts string values to integers.
    """
    test_env_vars = {
        "APP_NAME": "test-app",
        "ALLOWED_ORIGINS": "http://localhost",
        "APP_ENVIRONMENT": "test",
        "APP_DEBUG": "false",
        "LOG_LEVEL": "INFO",
        "LOG_CHANNEL": "stream",
        "LOG_DIR": "/tmp",
        "DB_TYPE": "postgres",
        "DB_DRIVER": "postgresql",
        "DB_HOST": "localhost",
        "DB_NAME": "testdb",
        "DB_USERNAME": "user",
        "DB_PASSWORD": "password"
    }

    # Test with valid port number
    test_env_vars["DB_PORT"] = "5432"
    for key, value in test_env_vars.items():
        os.environ[key] = value

    try:
        settings = EnvironmentVariables()
        assert settings.DB_PORT == 5432
        assert isinstance(settings.DB_PORT, int)
    finally:
        for key in test_env_vars.keys():
            os.environ.pop(key, None)

    # Test with invalid port number (should default to None)
    test_env_vars["DB_PORT"] = "invalid_port"
    for key, value in test_env_vars.items():
        os.environ[key] = value

    try:
        settings = EnvironmentVariables()
        assert settings.DB_PORT is None
    finally:
        for key in test_env_vars.keys():
            os.environ.pop(key, None)


def test_optional_fields_defaults():
    """
    Test that optional fields have correct default values.
    """
    test_env_vars = {
        "APP_NAME": "test-app",
        "ALLOWED_ORIGINS": "http://localhost",
        "APP_ENVIRONMENT": "test",
        "APP_DEBUG": "false",
        "LOG_LEVEL": "INFO",
        "LOG_CHANNEL": "stream",
        "LOG_DIR": "/tmp",
        "DB_TYPE": "sqlite",
        "DB_DRIVER": "sqlite",
        "DB_HOST": "localhost",
        "DB_NAME": "test.db",
        "DB_USERNAME": "test",
        "DB_PASSWORD": "test"
    }

    for key, value in test_env_vars.items():
        os.environ[key] = value

    try:
        settings = EnvironmentVariables()

        # Test default values for optional fields
        assert settings.APP_MAINTENANCE is False
        assert settings.DB_PORT is None
        assert settings.DB_SSL_CA is None
        assert settings.DB_SSL_VERIFY_CERT is None
    finally:
        for key in test_env_vars.keys():
            os.environ.pop(key, None)
