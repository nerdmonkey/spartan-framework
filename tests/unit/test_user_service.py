import pytest
from unittest.mock import MagicMock
from datetime import datetime
from app.services.user import UserService
from app.models.user import User
from app.requests.user import UserCreateRequest, UserUpdateRequest
from app.exceptions.user import UserNotFoundError, DuplicateUserError

@pytest.fixture
def mock_db_session():
    session = MagicMock()
    session.query.return_value.filter.return_value.first.return_value = None  # Default to no user found
    session.add = MagicMock()
    session.commit = MagicMock()
    session.refresh = MagicMock()
    session.delete = MagicMock()
    return session

@pytest.fixture
def user_service(mock_db_session):
    return UserService(mock_db_session)

@pytest.fixture
def user_create_request():
    return UserCreateRequest(
        username="testuser",
        email="testuser@example.com",
        password="securepassword123"
    )

@pytest.fixture
def user_update_request():
    return UserUpdateRequest(
        username="updateduser",
        email="updateduser@example.com",
        password="newsecurepassword123"
    )

def test_get_by_id(user_service, mock_db_session):
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user.username = "testuser"
    mock_user.email = "testuser@example.com"
    mock_user.created_at = "2023-01-01 00:00:00"
    mock_user.updated_at = "2023-01-01 00:00:00"
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user

    result = user_service.get_by_id(1)
    assert result.id == 1
    assert result.username == "testuser"

def test_get_by_id_not_found(user_service, mock_db_session):
    mock_db_session.query.return_value.filter.return_value.first.return_value = None
    with pytest.raises(UserNotFoundError):
        user_service.get_by_id(999)

def test_save_user(user_service, user_create_request, mock_db_session):
    mock_db_session.query.return_value.filter.return_value.first.return_value = None  # Ensure user does not exist
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user.username = user_create_request.username
    mock_user.email = user_create_request.email
    mock_user.created_at = "2023-01-01 00:00:00"
    mock_user.updated_at = "2023-01-01 00:00:00"
    mock_db_session.refresh.side_effect = lambda x: setattr(x, 'id', 1)
    mock_db_session.add.side_effect = lambda x: setattr(x, 'created_at', "2023-01-01 00:00:00")
    mock_db_session.add.side_effect = lambda x: setattr(x, 'updated_at', "2023-01-01 00:00:00")

    response = user_service.save(user_create_request)
    assert response.username == user_create_request.username
    assert response.email == user_create_request.email

def test_save_duplicate_user(user_service, user_create_request, mock_db_session):
    mock_user = MagicMock()
    mock_user.username = "testuser"
    mock_user.email = "testuser@example.com"
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user

    with pytest.raises(DuplicateUserError):
        user_service.save(user_create_request)

def test_update_user(user_service, user_update_request, mock_db_session):
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user.username = "testuser"
    mock_user.email = "testuser@example.com"
    mock_user.created_at = "2023-01-01 00:00:00"
    mock_user.updated_at = "2023-01-01 00:00:00"
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user

    response = user_service.update(1, user_update_request)
    assert response.username == user_update_request.username
    assert response.email == user_update_request.email
    assert response.updated_at == "2023-01-01 00:00:00"

def test_update_user_not_found(user_service, user_update_request, mock_db_session):
    mock_db_session.query.return_value.filter.return_value.first.return_value = None
    with pytest.raises(UserNotFoundError):
        user_service.update(999, user_update_request)

def test_delete_user(user_service, mock_db_session):
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user.username = "testuser"
    mock_user.email = "testuser@example.com"
    mock_user.created_at = "2023-01-01 00:00:00"
    mock_user.updated_at = "2023-01-01 00:00:00"
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user

    response = user_service.delete(1)
    assert response.id == 1
    assert response.username == "testuser"

def test_delete_user_not_found(user_service, mock_db_session):
    mock_db_session.query.return_value.filter.return_value.first.return_value = None
    with pytest.raises(UserNotFoundError):
        user_service.delete(999)

# Additional Edge Case Tests
def test_save_user_missing_fields(user_service):
    with pytest.raises(ValueError):  # Assuming service validates input
        user_service.save(UserCreateRequest(username="", email="", password=""))

def test_save_user_invalid_email(user_service):
    with pytest.raises(ValueError):  # Assuming service validates email format
        user_service.save(UserCreateRequest(username="test", email="invalid-email", password="password123"))
