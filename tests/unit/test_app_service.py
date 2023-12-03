from unittest.mock import MagicMock, patch

import jsonpickle
import pytest
from botocore.exceptions import BotoCoreError

from app.services.app import AppService


@pytest.fixture
def mock_dynamodb_resource(mocker):
    return mocker.patch("boto3.resource")


@pytest.fixture
def mock_table():
    table = MagicMock()
    table.name = "test_table"
    return table


@pytest.fixture
def app_service(mock_dynamodb_resource, mock_table):
    mock_dynamodb_resource.return_value.Table.return_value = mock_table
    service = AppService()
    return service


def test_set_state_success(app_service, mock_table):
    """Test setting state successfully."""
    mock_table.update_item.return_value = {
        "Attributes": {"Attr_Data": "serialized_data"}
    }
    response = app_service.set_state("test_key", {"some": "data"})
    assert response == "serialized_data"


def test_set_state_error(app_service, mock_table):
    """Test error during setting state."""
    mock_table.update_item.side_effect = BotoCoreError
    with pytest.raises(BotoCoreError):
        app_service.set_state("test_key", {"some": "data"})


def test_get_state_success(app_service, mock_table):
    """Test retrieving state successfully."""
    test_data = {"some": "data"}
    serialized_data = jsonpickle.encode(test_data)
    mock_table.get_item.return_value = {"Item": {"Attr_Data": serialized_data}}
    response = app_service.get_state("test_key")
    assert response == test_data


def test_get_state_not_found(app_service, mock_table):
    """Test retrieving state that doesn't exist."""
    mock_table.get_item.return_value = {}
    response = app_service.get_state("missing_key")
    assert response is None


def test_remove_state_success(app_service, mock_table):
    """Test removing state successfully."""
    mock_table.delete_item.return_value = {}
    response = app_service.remove_state("test_key")
    assert response is None


# Additional tests for error handling in get_state and remove_state can be added here.
