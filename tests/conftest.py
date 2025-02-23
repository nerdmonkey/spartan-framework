import logging
import os
import tempfile
from datetime import datetime
from unittest.mock import Mock, patch

import pytest
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.helpers.database import db
from app.helpers.logger.file import FileLogger
from app.models.base import Base
from app.models.user import User

load_dotenv(dotenv_path=".env_testing")

get_db = db()


def construct_database_url():
    db_type = os.environ.get("DB_TYPE", "sqlite")
    db_name = "spartan.db"
    if db_type == "sqlite":
        return f"sqlite:///./database/{db_name}"
    else:
        db_host = os.getenv("DB_HOST", "localhost")
        db_port = os.getenv("DB_PORT", "5432")
        db_username = os.getenv("DB_USERNAME", "user")
        db_password = os.getenv("DB_PASSWORD", "password")

        if db_type == "psql":
            return f"postgresql://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}"

        elif db_type == "mysql":
            return f"mysql+pymysql://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}"
        else:
            raise ValueError(f"Unsupported database type: {db_type}")

    raise ValueError(f"Unsupported database type: {db_type}")


@pytest.fixture(scope="module")
def test_db_session():
    TEST_DATABASE_URL = construct_database_url()

    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=engine
    )

    db = TestingSessionLocal()

    yield db

    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="module")
def test_data(test_db_session):
    users = [
        User(
            username=f"testuser{i}",
            email=f"testuser{i}@example.com",
            password="password123",
        )
        for i in range(1, 6)
    ]

    for user in users:
        test_db_session.add(user)
    test_db_session.commit()

    yield users

    for user in users:
        test_db_session.delete(user)
    test_db_session.commit()


@pytest.fixture
def temp_log_dir():
    """Create a temporary directory for log files"""
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield tmpdirname


@pytest.fixture
def mock_datetime():
    """Mock datetime to return a fixed value"""
    fixed_datetime = datetime(2023, 12, 20, 10, 30, 0)
    with patch("app.helpers.logger.file.datetime") as mock_dt:
        mock_dt.utcnow.return_value = fixed_datetime
        yield mock_dt


@pytest.fixture
def file_logger(temp_log_dir):
    """Create a FileLogger instance with temporary directory"""
    logger = FileLogger(
        service_name="test-service",
        level="DEBUG",
        log_dir=temp_log_dir,
        max_bytes=1024,  # Small size for testing rotation
        backup_count=2,
    )
    return logger


@pytest.fixture
def mock_logger():
    """Mock the underlying logger object"""
    with patch("logging.getLogger") as mock_get_logger:
        mock_logger = Mock(spec=logging.Logger)
        mock_get_logger.return_value = mock_logger
        yield mock_logger


@pytest.fixture(autouse=True)
def _setup_testing_environment():
    """Setup any necessary test environment variables"""
    yield


@pytest.fixture(autouse=True)
def _prevent_external_calls(monkeypatch):
    """Prevent any accidental external calls during testing"""

    def mock_external_call(*args, **kwargs):
        raise RuntimeError("External calls are not allowed during testing")

    # Add any external calls you want to prevent
    monkeypatch.setattr("socket.socket", mock_external_call)


@pytest.fixture
def mock_tracer_config():
    """Fixture to provide standard tracer configuration"""
    return {"service_name": "test_service", "environment": "test"}


@pytest.fixture
def mock_env_cloud():
    """Fixture to mock environment for cloud configuration"""

    def mock_getenv(key, default=None):  # Add default parameter
        if key == "TRACER_TYPE":
            return "cloud"
        if key == "SERVICE_NAME":
            return "test_service"
        return default  # Return default instead of None

    with patch(
        "app.helpers.tracer.factory.os.getenv", side_effect=mock_getenv
    ) as mock:
        yield mock
