import pytest
from unittest.mock import patch
from config.app import get_settings
from sqlalchemy.engine import Engine
from config.database import get_session  # Replace 'your_module' with the actual module name

def test_get_session():
    """
    Test the get_session function to ensure it returns a SQLAlchemy session.

    This test mocks the get_settings function to return test settings and verifies
    that the get_session function returns a session object. It uses an in-memory
    SQLite database for testing to avoid side effects on the actual database.
    """
    test_settings = {
        'DB_NAME': 'test_db',
        'DB_TYPE': 'sqlite',
        'DB_HOST': '',
        'DB_PORT': '',
        'DB_USERNAME': '',
        'DB_PASSWORD': '',
    }

    with patch('config.app.get_settings', return_value=test_settings):
        session = get_session()

        assert session is not None
        assert isinstance(session.bind, Engine)
