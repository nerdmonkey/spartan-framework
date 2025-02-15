import pytest

from app.requests.user import UserCreateRequest, UserUpdateRequest


@pytest.fixture
def user_request_data():
    return {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "securepassword123",
    }


def test_user_create_request_creation(user_request_data):
    user_request = UserCreateRequest(**user_request_data)
    assert user_request.username == user_request_data["username"]
    assert user_request.email == user_request_data["email"]
    assert user_request.password == user_request_data["password"]


def test_user_create_request_missing_username(user_request_data):
    user_request_data.pop("username")
    with pytest.raises(ValueError):
        UserCreateRequest(**user_request_data)


def test_user_create_request_missing_email(user_request_data):
    user_request_data.pop("email")
    with pytest.raises(ValueError):
        UserCreateRequest(**user_request_data)


def test_user_create_request_missing_password(user_request_data):
    user_request_data.pop("password")
    with pytest.raises(ValueError):
        UserCreateRequest(**user_request_data)


def test_user_create_request_invalid_email_format(user_request_data):
    user_request_data["email"] = "invalid-email-format"
    with pytest.raises(ValueError):
        UserCreateRequest(**user_request_data)


def test_user_update_request_creation(user_request_data):
    user_request = UserUpdateRequest(**user_request_data)
    assert user_request.username == user_request_data["username"]
    assert user_request.email == user_request_data["email"]
    assert user_request.password == user_request_data["password"]


def test_user_update_request_partial_update(user_request_data):
    partial_data = {"email": "newemail@example.com"}
    user_request = UserUpdateRequest(**partial_data)
    assert user_request.email == partial_data["email"]
    assert user_request.username is None
    assert user_request.password is None


def test_user_update_request_invalid_email_format(user_request_data):
    user_request_data["email"] = "invalid-email-format"
    with pytest.raises(ValueError):
        UserUpdateRequest(**user_request_data)
