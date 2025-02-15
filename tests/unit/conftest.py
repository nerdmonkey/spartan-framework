import pytest


@pytest.fixture
def user_request_data():
    return {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "securepassword123",
    }
