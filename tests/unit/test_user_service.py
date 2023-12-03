import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.user import User
from app.requests.user import UserCreateRequest, UserUpdateRequest
from app.responses.user import UserCreateResponse, UserResponse, UserUpdateResponse
from app.services.user import UserService


# Create a mock database session for testing
@pytest.fixture
def mock_db_session():
    class MockSession:
        def __init__(self):
            self.users = []

        def query(self, model):
            return self

        def filter(self, condition):
            return self

        def first(self):
            return self.users[0] if self.users else None

        def all(self):
            return self.users

        def offset(self, offset):
            return self

        def limit(self, limit):
            return self

        def add(self, item):
            self.users.append(item)

        def commit(self):
            pass

        def refresh(self, item):
            pass

        def delete(self, item):
            self.users.remove(item)

    return MockSession()


# Tests for UserService
def test_get_by_id(mock_db_session):
    user1 = User(id=1, username="user1", email="user1@example.com")
    mock_db_session.users.append(user1)
    user_service = UserService(db=mock_db_session)

    result = user_service.get_by_id(1)

    assert result == user1


def test_get_by_id_not_found(mock_db_session):
    user_service = UserService(db=mock_db_session)

    with pytest.raises(HTTPException):
        user_service.get_by_id(1)


def test_all(mock_db_session):
    user1 = User(id=1, username="user1", email="user1@example.com")
    user2 = User(id=2, username="user2", email="user2@example.com")
    mock_db_session.users.extend([user1, user2])
    user_service = UserService(db=mock_db_session)

    result = user_service.all(page=1, items_per_page=2)

    assert len(result) == 2
    assert result[0].id == user1.id
    assert result[1].id == user2.id


def test_get(mock_db_session):
    user1 = User(id=1, username="user1", email="user1@example.com")
    mock_db_session.users.append(user1)
    user_service = UserService(db=mock_db_session)

    result = user_service.find(1)

    assert result.id == user1.id


def test_get_not_found(mock_db_session):
    user_service = UserService(db=mock_db_session)

    with pytest.raises(HTTPException):
        user_service.find(1)


def test_create(mock_db_session):
    user_create_request = UserCreateRequest(
        username="new", email="new@example.com", password="password"
    )
    user_service = UserService(db=mock_db_session)

    result = user_service.save(user_create_request)

    assert result is not None
    assert "id" in result
    assert result["username"] == user_create_request.username
    assert result["email"] == user_create_request.email


def test_create_duplicate_email(mock_db_session):
    user1 = User(id=1, username="user1", email="user1@example.com")
    user_create_request = UserCreateRequest(
        username="user1", email="user1@example.com", password="password"
    )
    mock_db_session.users.append(user1)
    user_service = UserService(db=mock_db_session)

    with pytest.raises(HTTPException):
        user_service.save(user_create_request)


def test_update(mock_db_session):
    user1 = User(id=1, username="user1", email="user1@example.com")
    user_update_request = UserUpdateRequest(
        username="updated", email="updated@example.com", password="new_password"
    )
    mock_db_session.users.append(user1)
    user_service = UserService(db=mock_db_session)

    result = user_service.update(1, user_update_request)

    assert result["id"] == user1.id
    assert result["username"] == user_update_request.username
    assert result["email"] == user_update_request.email


def test_update_not_found(mock_db_session):
    user_update_request = UserUpdateRequest(
        username="updated", email="updated@example.com", password="new_password"
    )
    user_service = UserService(db=mock_db_session)

    with pytest.raises(HTTPException):
        user_service.update(1, user_update_request)


def test_delete(mock_db_session):
    user1 = User(id=1, username="user1", email="user1@example.com")
    mock_db_session.users.append(user1)
    user_service = UserService(db=mock_db_session)

    user_service.delete(1)

    assert len(mock_db_session.users) == 0


def test_delete_not_found(mock_db_session):
    user_service = UserService(db=mock_db_session)

    with pytest.raises(HTTPException):
        user_service.delete(1)
