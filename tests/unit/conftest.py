import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.models.base import Base


@pytest.fixture(scope="module")
def db_engine():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture(scope="function")
def db_session(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    SessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=db_engine
    )
    session = SessionLocal()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def user_request_data():
    return {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "securepassword123",
    }
