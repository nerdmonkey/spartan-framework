import os
import pytest
from unittest.mock import Mock, patch
import logging
import tempfile
from datetime import datetime

import pytest
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.helpers.logger.file import FileLogger
from app.helpers.database import db
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
    with patch('app.helpers.logger.file.datetime') as mock_dt:
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
        backup_count=2
    )
    return logger

@pytest.fixture
def mock_logger():
    """Mock the underlying logger object"""
    with patch('logging.getLogger') as mock_get_logger:
        mock_logger = Mock(spec=logging.Logger)
        mock_get_logger.return_value = mock_logger
        yield mock_logger
