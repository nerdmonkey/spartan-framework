from unittest.mock import MagicMock

import pytest
from datetime import datetime

from app.exceptions.user import DuplicateUserError, UserNotFoundError
from app.models.user import User
from app.requests.user import UserCreateRequest, UserUpdateRequest
from app.services.user import UserService


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
        password="securepassword123",
    )


@pytest.fixture
def user_update_request():
    return UserUpdateRequest(
        username="updateduser",
        email="updateduser@example.com",
        password="newsecurepassword123",
    )


class TestUserService:
    def setup_method(self):
        self.mock_db_session = MagicMock()
        self.mock_db_session.query.return_value.filter.return_value.first.return_value = None  # Default to no user found
        self.mock_db_session.add = MagicMock()
        self.mock_db_session.commit = MagicMock()
        self.mock_db_session.refresh = MagicMock()
        self.mock_db_session.delete = MagicMock()
        self.user_service = UserService(self.mock_db_session)

    def teardown_method(self):
        self.mock_db_session.reset_mock()

    def test_get_by_id(self):
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.username = "testuser"
        mock_user.email = "testuser@example.com"
        mock_user.created_at = datetime(2023, 1, 1, 0, 0, 0)
        mock_user.updated_at = datetime(2023, 1, 1, 0, 0, 0)
        mock_user.created_at.strftime = MagicMock(return_value="2023-01-01 00:00:00")
        mock_user.updated_at.strftime = MagicMock(return_value="2023-01-01 00:00:00")
        self.mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user

        result = self.user_service.get_by_id(1)
        assert result.id == 1
        assert result.username == "testuser"

    def test_get_by_id_not_found(self):
        self.mock_db_session.query.return_value.filter.return_value.first.return_value = None
        with pytest.raises(UserNotFoundError):
            self.user_service.get_by_id(999)

    def test_save_user(self, user_create_request):
        self.mock_db_session.query.return_value.filter.return_value.first.return_value = None  # Ensure user does not exist
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.username = user_create_request.username
        mock_user.email = user_create_request.email
        mock_user.created_at = datetime(2023, 1, 1, 0, 0, 0)
        mock_user.updated_at = datetime(2023, 1, 1, 0, 0, 0)
        mock_user.created_at.strftime = MagicMock(return_value="2023-01-01 00:00:00")
        mock_user.updated_at.strftime = MagicMock(return_value="2023-01-01 00:00:00")
        self.mock_db_session.refresh.side_effect = lambda x: setattr(x, 'id', 1)
        self.mock_db_session.add.side_effect = lambda x: setattr(x, 'created_at', datetime(2023, 1, 1, 0, 0, 0))
        self.mock_db_session.add.side_effect = lambda x: setattr(x, 'updated_at', datetime(2023, 1, 1, 0, 0, 0))

        response = self.user_service.save(user_create_request)
        assert response.username == user_create_request.username
        assert response.email == user_create_request.email

    def test_save_duplicate_user(self, user_create_request):
        mock_user = MagicMock()
        mock_user.username = "testuser"
        mock_user.email = "testuser@example.com"
        self.mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user

        with pytest.raises(DuplicateUserError):
            self.user_service.save(user_create_request)

    def test_update_user(self, user_update_request):
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.username = "testuser"
        mock_user.email = "testuser@example.com"
        mock_user.created_at = datetime(2023, 1, 1, 0, 0, 0)
        mock_user.updated_at = datetime(2023, 1, 1, 0, 0, 0)
        mock_user.created_at.strftime = MagicMock(return_value="2023-01-01 00:00:00")
        mock_user.updated_at.strftime = MagicMock(return_value="2023-01-01 00:00:00")
        self.mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user

        response = self.user_service.update(1, user_update_request)
        assert response.username == user_update_request.username
        assert response.email == user_update_request.email
        assert response.updated_at == "2023-01-01 00:00:00"

    def test_update_user_not_found(self, user_update_request):
        self.mock_db_session.query.return_value.filter.return_value.first.return_value = None
        with pytest.raises(UserNotFoundError):
            self.user_service.update(999, user_update_request)

    def test_delete_user(self):
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.username = "testuser"
        mock_user.email = "testuser@example.com"
        mock_user.created_at = datetime(2023, 1, 1, 0, 0, 0)
        mock_user.updated_at = datetime(2023, 1, 1, 0, 0, 0)
        mock_user.created_at.strftime = MagicMock(return_value="2023-01-01 00:00:00")
        mock_user.updated_at.strftime = MagicMock(return_value="2023-01-01 00:00:00")
        self.mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user

        response = self.user_service.delete(1)
        assert response.id == 1
        assert response.username == "testuser"

    def test_delete_user_not_found(self):
        self.mock_db_session.query.return_value.filter.return_value.first.return_value = None
        with pytest.raises(UserNotFoundError):
            self.user_service.delete(999)

    # Additional Edge Case Tests
    def test_save_user_missing_fields(self):
        with pytest.raises(ValueError):  # Assuming service validates input
            self.user_service.save(UserCreateRequest(username="", email="", password=""))

    def test_save_user_invalid_email(self):
        with pytest.raises(ValueError):  # Assuming service validates email format
            self.user_service.save(
                UserCreateRequest(
                    username="test", email="invalid-email", password="password123"
                )
            )
