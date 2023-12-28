import pytest
from fastapi import HTTPException

from app.models.user import User
from app.services.user import UserService
from app.requests.user import UserCreateRequest, UserUpdateRequest

# Create a mock database session for testing
@pytest.fixture
def mock_db_session():
    class MockSession:
        def __init__(self):
            self.users = []

        def query(self, model):
            return self

        def filter(self, condition):
            self.query_condition = (
                condition.right.value
            )  # Assuming condition is User.id == id
            return self

        def filter(self, condition):
            # Assume the condition is structured like User.email == email
            attribute = condition.left.key
            value = condition.right.value

            self.filtered_users = [
                user for user in self.users if getattr(user, attribute) == value
            ]
            return self

        def first(self):
            return self.filtered_users[0] if self.filtered_users else None

        def offset(self, offset):
            self.pagination_offset = offset
            return self

        def limit(self, limit):
            self.pagination_limit = limit
            return self

        def all(self):
            start = self.pagination_offset
            end = start + self.pagination_limit
            return self.users[start:end]

        def count(self):
            return len(self.users)

        def add(self, item):
            self.users.append(item)

        def commit(self):
            pass

        def refresh(self, item):
            pass

        def delete(self, item):
            self.users.remove(item)

    return MockSession()


# Helper function to add users to mock_db_session
def add_users_to_session(session, num_users):
    for i in range(1, num_users + 1):
        user = User(id=i, username=f"user{i}", email=f"user{i}@example.com")
        session.users.append(user)


# Tests for UserService
@pytest.mark.parametrize("user_id, expected_result", [(1, True), (99, False)])
def test_get_by_id(mock_db_session, user_id, expected_result):
    add_users_to_session(mock_db_session, 5)
    user_service = UserService(db=mock_db_session)

    if expected_result:
        result = user_service.get_by_id(user_id)
        assert result.id == user_id
    else:
        with pytest.raises(HTTPException) as exc_info:
            user_service.get_by_id(user_id)
        assert exc_info.value.status_code == 404


def test_all_with_pagination(mock_db_session):
    add_users_to_session(mock_db_session, 10)
    user_service = UserService(db=mock_db_session)

    result, total = user_service.all(page=2, items_per_page=5)

    assert len(result) == 5
    assert total == 10


def test_total(mock_db_session):
    add_users_to_session(mock_db_session, 3)
    user_service = UserService(db=mock_db_session)

    result = user_service.total()

    assert result == 3


def test_find_user(mock_db_session):
    # Adding a user to the mock session
    user1 = User(id=1, username="user1", email="user1@example.com")
    mock_db_session.users.append(user1)

    user_service = UserService(db=mock_db_session)

    # Finding the user by id
    result = user_service.find(1)

    # Assertions
    assert result.id == 1
    assert result.username == "user1"


def test_save_user(mock_db_session):
    user_service = UserService(db=mock_db_session)
    user_request = UserCreateRequest(
        username="new_user", email="new_user@example.com", password="password"
    )

    result = user_service.save(user_request)

    assert result["username"] == user_request.username
    assert result["email"] == user_request.email
    assert len(mock_db_session.users) == 1


def test_save_duplicate_email_user(mock_db_session):
    add_users_to_session(mock_db_session, 1)
    user_service = UserService(db=mock_db_session)
    user_request = UserCreateRequest(
        username="user2", email="user1@example.com", password="password"
    )

    with pytest.raises(HTTPException) as exc_info:
        user_service.save(user_request)
    assert exc_info.value.status_code == 422


def test_update_user(mock_db_session):
    add_users_to_session(mock_db_session, 1)
    user_service = UserService(db=mock_db_session)
    user_request = UserUpdateRequest(
        username="updated_user", email="updated_user@example.com"
    )

    result = user_service.update(1, user_request)

    assert result["username"] == user_request.username
    assert result["email"] == user_request.email


def test_update_nonexistent_user(mock_db_session):
    user_service = UserService(db=mock_db_session)
    user_request = UserUpdateRequest(username="user2", email="user2@example.com")

    with pytest.raises(HTTPException) as exc_info:
        user_service.update(2, user_request)
    assert exc_info.value.status_code == 404


def test_delete_user(mock_db_session):
    add_users_to_session(mock_db_session, 1)
    user_service = UserService(db=mock_db_session)

    user_service.delete(1)

    assert len(mock_db_session.users) == 0


def test_delete_nonexistent_user(mock_db_session):
    user_service = UserService(db=mock_db_session)

    with pytest.raises(HTTPException) as exc_info:
        user_service.delete(2)
    assert exc_info.value.status_code == 404
