import pytest
from unittest.mock import MagicMock
from app.services.user import UserService
from app.models.user import User
from config.database import Session

class TestUserService:
    def test_all(self, mocker):
        """
        Test the all method of UserService.
        This test ensures that the all method queries the User model for all records.
        It mocks the Session and query to prevent database access.
        """
        # Mock the session instance and its query method
        mocked_session = mocker.MagicMock()
        mocked_session.query.return_value.all.return_value = []
        mocker.patch('app.services.user.Session', return_value=mocked_session)

        service = UserService()
        result = service.all()

        assert result == []

    def test_find(self, mocker):
        """
        Test the find method of UserService.
        This test ensures that the find method queries the User model for a specific record by ID.
        It mocks the Session and query to prevent database access.
        """
        # Mock the session instance and its query method
        mocked_session = mocker.MagicMock()
        mocked_session.query.return_value.filter_by.return_value.first.return_value = None
        mocker.patch('app.services.user.Session', return_value=mocked_session)

        service = UserService()
        result = service.find(1)

        assert result is None


    def test_save(self, mocker):
        """
        Test the save method of UserService.
        This test ensures that the save method adds a new record to the User model.
        It mocks the Session and the add, commit, and refresh methods to prevent database access.
        """
        # Mock the session instance and its methods
        mocked_session = mocker.MagicMock()
        mocker.patch('app.services.user.Session', return_value=mocked_session)

        # Mock User object to simulate database save and refresh
        mocked_user = User(id=1, username='test', email='test@example.com')
        mocker.patch('app.services.user.User', return_value=mocked_user)

        service = UserService()
        new_user_id = service.save({'username': 'test', 'email': 'test@example.com'})

        assert new_user_id == 1  # Assuming the User's id is set to 1
