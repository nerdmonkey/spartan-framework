from datetime import datetime, timedelta

import pytest

from app.exceptions.user import (
    DuplicateUserError,
    InvalidSortFieldError,
    UserNotFoundError,
)
from app.models.user import User
from app.requests.user import UserCreateRequest, UserUpdateRequest
from app.responses.user import UserCreateResponse, UserResponse, UserUpdateResponse
from app.services.user import UserService


class MockSession:
    def __init__(self):
        self.users = []
        self.filtered_users = self.users

    def query(self, model):
        self.filtered_users = self.users  # Reset to all users on new query
        return self

    def filter(self, condition):
        if hasattr(condition, "right") and hasattr(condition.right, "value"):
            value = condition.right.value
            if hasattr(condition.left, "key"):
                attribute = condition.left.key
                self.filtered_users = [
                    user
                    for user in self.filtered_users
                    if getattr(user, attribute) == value
                ]
            else:
                self.filtered_users = [
                    user for user in self.filtered_users if user.id == value
                ]
        return self

    def filter_by_field(self, field, value):
        self.filtered_users = [
            user for user in self.filtered_users if getattr(user, field) == value
        ]
        return self

    def filter_by_date_range(self, field, start_date, end_date):
        self.filtered_users = [
            user
            for user in self.filtered_users
            if start_date <= getattr(user, field) <= end_date
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
        start = getattr(self, "pagination_offset", 0)
        end = start + getattr(self, "pagination_limit", len(self.filtered_users))
        return self.filtered_users[start:end]

    def count(self):
        return len(self.filtered_users)

    def add(self, item):
        if not hasattr(item, "id") or item.id is None:
            item.id = len(self.users) + 1
        if not hasattr(item, "created_at") or item.created_at is None:
            item.created_at = datetime.now()
        if not hasattr(item, "updated_at") or item.updated_at is None:
            item.updated_at = datetime.now()
        self.users.append(item)

    def refresh(self, item):
        if not item.created_at:
            item.created_at = datetime.now()
        if not item.updated_at:
            item.updated_at = datetime.now()

    def commit(self):
        pass

    def delete(self, item):
        self.users.remove(item)

    def order_by(self, *args, **kwargs):
        field = args[0]
        descending = kwargs.get("descending", False)
        self.filtered_users = sorted(
            self.filtered_users, key=lambda x: getattr(x, field), reverse=descending
        )
        return self


@pytest.fixture
def mock_db_session():
    return MockSession()


def create_test_user(
    id=1,
    username="testuser",
    email="testuser@example.com",
    created_at=None,
    updated_at=None,
):
    return User(
        id=id,
        username=username,
        email=email,
        created_at=created_at or datetime.now() - timedelta(days=1),
        updated_at=updated_at or datetime.now(),
    )


def test_get_by_id(mock_db_session):
    mock_db_session.add(create_test_user())
    user_service = UserService(db=mock_db_session)
    user = user_service.get_by_id(1)
    assert user.id == 1
    assert user.username == "testuser"

    # Test user not found
    with pytest.raises(UserNotFoundError):
        user_service.get_by_id(999)


def test_all_with_pagination_and_sorting(mock_db_session):
    for i in range(10, 0, -1):  # Adding users with IDs from 10 to 1
        mock_db_session.add(create_test_user(id=i))

    user_service = UserService(db=mock_db_session)
    users, total, last_page, first_item, last_item = user_service.all(
        1, 5, sort_type="desc", sort_by="id"
    )

    assert len(users) == 5
    assert total == 10
    assert last_page == 2
    assert first_item == 1
    assert last_item == 5
    assert users[0].id == 10
    assert users[-1].id == 6


def test_invalid_sort_field(mock_db_session):
    user_service = UserService(db=mock_db_session)
    with pytest.raises(InvalidSortFieldError):
        user_service.all(1, 5, sort_by="invalid_field")


def test_filter_users_by_username(mock_db_session):
    mock_db_session.add(create_test_user(id=5, username="user5"))

    user_service = UserService(db=mock_db_session)
    users, _, _, _, _ = user_service.all(1, 10, username="user5")

    assert len(users) == 1
    assert users[0].username == "user5"


def test_filter_users_by_date(mock_db_session):
    # Create two users, one with a date outside the range and one within it
    user_older = create_test_user(
        id=1, username="olduser", created_at=datetime.now() - timedelta(days=10)
    )
    user_newer = create_test_user(id=2, username="newuser", created_at=datetime.now())

    # Add users to the session
    mock_db_session.add(user_older)
    mock_db_session.add(user_newer)

    # Set the date range to include only `user_newer`
    user_service = UserService(db=mock_db_session)
    start_date = datetime.now() - timedelta(days=5)  # datetime object, not string
    end_date = datetime.now()  # datetime object

    # Call the `all` method with the specified date range
    users, _, _, _, _ = user_service.all(
        1, 10, start_date=start_date, end_date=end_date
    )

    # Assert that only `user_newer` is returned
    assert len(users) == 1
    assert users[0].username == "newuser"


def test_total_users(mock_db_session):
    for i in range(3):
        mock_db_session.add(create_test_user(id=i + 1))
    user_service = UserService(db=mock_db_session)
    assert user_service.total() == 3


def test_save_user(mock_db_session):
    user_service = UserService(db=mock_db_session)
    user_request = UserCreateRequest(
        username="testnewuser", email="new_user@example.com", password="password"
    )
    saved_user = user_service.save(user_request)

    assert isinstance(saved_user, UserCreateResponse)
    assert saved_user.username == "testnewuser"
    assert saved_user.email == "new_user@example.com"


def test_save_duplicate_user(mock_db_session):
    mock_db_session.add(create_test_user(email="duplicate@example.com"))
    user_service = UserService(db=mock_db_session)
    user_request = UserCreateRequest(
        username="duplicateuser", email="duplicate@example.com", password="password"
    )

    with pytest.raises(DuplicateUserError):
        user_service.save(user_request)


def test_update_user(mock_db_session):
    mock_db_session.add(create_test_user())
    user_service = UserService(db=mock_db_session)
    user_request = UserUpdateRequest(
        username="updateduser", email="updated_user@example.com"
    )
    updated_user = user_service.update(1, user_request)

    assert isinstance(updated_user, UserUpdateResponse)
    assert updated_user.username == "updateduser"
    assert updated_user.email == "updated_user@example.com"


def test_update_user_not_found(mock_db_session):
    user_service = UserService(db=mock_db_session)
    user_request = UserUpdateRequest(
        username="updateduser", email="updated_user@example.com"
    )

    with pytest.raises(UserNotFoundError):
        user_service.update(999, user_request)


def test_delete_user(mock_db_session):
    mock_db_session.add(create_test_user())
    user_service = UserService(db=mock_db_session)
    deleted_user = user_service.delete(1)

    assert isinstance(deleted_user, UserResponse)
    assert deleted_user.id == 1
    assert deleted_user.username == "testuser"


def test_delete_user_not_found(mock_db_session):
    user_service = UserService(db=mock_db_session)
    with pytest.raises(UserNotFoundError):
        user_service.delete(999)
