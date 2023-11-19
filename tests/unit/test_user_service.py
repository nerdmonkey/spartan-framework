import pytest
from unittest.mock import create_autospec, patch
from sqlalchemy.orm import Session
from app.models.user import User
from app.services.user import UserService

@pytest.fixture
def mock_session():
    # Create a mock session to simulate database interactions
    session = create_autospec(Session, instance=True)
    return session

@pytest.fixture
def user_service(mock_session):
    # Patch the Session object in user_service to use the mock session
    with patch('app.services.user.Session', return_value=mock_session):
        yield UserService()

def test_all_users(user_service, mock_session):
    """
    Test retrieving all users.
    """
    mock_session.query.return_value.all.return_value = [
        User(id=1, username='testuser1'),
        User(id=2, username='testuser2')
    ]
    users = user_service.all()
    assert len(users) == 2
    assert users[0].id == 1
    assert users[1].username == 'testuser2'

def test_find_user(user_service, mock_session):
    """
    Test finding a specific user.
    """
    mock_user = User(id=1, username='testuser')
    mock_session.query.return_value.filter_by.return_value.first.return_value = mock_user
    user = user_service.find(1)
    assert user.id == 1
    assert user.username == 'testuser'

def test_save_user(user_service, mock_session):
    """
    Test saving a new user.
    """
    user_service.save({'username': 'newuser', 'password': 'newpass'})
    mock_session.add.assert_called_once()
    mock_session.flush.assert_called_once()

def test_update_user(user_service, mock_session):
    """
    Test updating an existing user.
    """
    mock_user = User(id=1, username='olduser')
    mock_session.query.return_value.filter_by.return_value.first.return_value = mock_user
    updated_user = user_service.update(1, {'username': 'updateduser'})
    assert updated_user.username == 'updateduser'

def test_delete_user(user_service, mock_session):
    """
    Test deleting a user.
    """
    user_service.delete(1)
    mock_session.query.return_value.filter_by.return_value.delete.assert_called_once()

def test_update_nonexistent_user(user_service, mock_session):
    """
    Test updating a user that does not exist.
    """
    mock_session.query.return_value.filter_by.return_value.first.return_value = None
    with pytest.raises(ValueError):
        user_service.update(99, {'username': 'nonexistent'})

# Additional tests to cover failure scenarios and exception handling can be added here.
