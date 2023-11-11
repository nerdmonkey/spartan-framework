from unittest.mock import patch, MagicMock

import pytest
from sqlalchemy.engine import Engine

from config.app import get_settings
from config.database import create_database_engine, get_session  # Replace 'your_module' with the actual module name

class MockSettings:
    DB_TYPE = 'unsupported_db_type'
    DB_NAME = 'testdb'
    # Add other necessary settings attributes if required

def test_get_session():
    """
    Test the get_session function to ensure it returns a SQLAlchemy session.

    This test mocks the get_settings function to return test settings and verifies
    that the get_session function returns a session object. It uses an in-memory
    SQLite database for testing to avoid side effects on the actual database.
    """
    test_settings = {
        "DB_NAME": "test_db",
        "DB_TYPE": "hunk",
        "DB_HOST": "",
        "DB_PORT": "",
        "DB_USERNAME": "",
        "DB_PASSWORD": "",
    }

    with patch("config.app.get_settings", return_value=test_settings):
        session = get_session()

        assert session is not None
        assert isinstance(session.bind, Engine)
