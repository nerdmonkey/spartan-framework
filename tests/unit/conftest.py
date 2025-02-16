from unittest.mock import MagicMock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.base import Base
from app.models.user import User
from app.requests.user import UserCreateRequest, UserUpdateRequest


@pytest.fixture(scope="function")
def db_session():
    session = MagicMock()
    yield session
    session.reset_mock()


@pytest.fixture
def user_request_data():
    return {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "securepassword123",
    }


@pytest.fixture
def user_create_request():
    return UserCreateRequest(
        username="testuser",
        email="testuser@example.com",
        password="securepassword123",
    )


@pytest.fixture
def user_update_request():
    return UserUpdateRequest(
        username="updateduser",
        email="updateduser@example.com",
        password="newsecurepassword123",
    )


@pytest.fixture
def test_user(db_session, user_create_request):
    user = User(
        id=1,
        username=user_create_request.username,
        email=user_create_request.email,
        password=user_create_request.password,
        created_at="2023-01-01 00:00:00",
        updated_at="2023-01-01 00:00:00",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user
