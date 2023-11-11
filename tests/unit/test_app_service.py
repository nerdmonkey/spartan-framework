import pytest
import os
import boto3
from moto import mock_dynamodb
from app.services.app import AppService

@pytest.fixture
def app_service():
    """
    A pytest fixture that sets up a mocked DynamoDB environment and AppService instance for testing.

    This fixture sets dummy AWS credentials and environment variables required for the AppService.
    It uses the 'moto' library to mock a DynamoDB environment and creates a test table.
    After setting up the environment, it yields an instance of the AppService class for use in tests.

    Yields:
        AppService: An instance of AppService configured to interact with the mocked DynamoDB.
    """
    # Set dummy AWS credentials for testing
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"

    # Setup environment variables for your service
    os.environ["GSM_TABLE"] = "testGlobalStateTable"
    os.environ["AWS_REGION"] = "us-east-1"

    # Create AppService instance
    service = AppService()

    # Setup DynamoDB mock
    with mock_dynamodb():  # or mock_dynamodb2 if you have resolved the import issue
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        dynamodb.create_table(
            TableName="testGlobalStateTable",
            KeySchema=[{'AttributeName': 'Key', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'Key', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )
        yield service

def test_set_state(app_service):
    """
    Test to ensure the set_state method of AppService correctly sets a state in the mocked DynamoDB.

    Args:
        app_service (AppService): The fixture providing an instance of AppService.

    Asserts:
        The response from set_state is not None, indicating a successful state set operation.
    """
    key = "testKey"
    value = {"data": "testValue"}

    # Test set_state
    response = app_service.set_state(key, value)

    # Assert
    assert response is not None

def test_get_state(app_service):
    """
    Test to ensure the get_state method of AppService correctly retrieves a state from the mocked DynamoDB.

    This test first sets a state using set_state and then attempts to retrieve it using get_state.

    Args:
        app_service (AppService): The fixture providing an instance of AppService.

    Asserts:
        The retrieved state matches the value initially set.
    """
    key = "testKey"
    value = {"data": "testValue"}

    # First set a state
    app_service.set_state(key, value)

    # Test get_state
    response = app_service.get_state(key)

    # Assert
    assert response == value

def test_remove_state(app_service):
    """
    Test to ensure the remove_state method of AppService correctly removes a state from the mocked DynamoDB.

    This test first sets a state, removes it, and then asserts that retrieving the state returns None.

    Args:
        app_service (AppService): The fixture providing an instance of AppService.

    Asserts:
        After removal, the state can no longer be retrieved (get_state returns None).
    """
    key = "testKey"
    value = {"data": "testValue"}

    # First set a state
    app_service.set_state(key, value)

    # Test remove_state
    app_service.remove_state(key)

    # Assert that the state is actually removed
    assert app_service.get_state(key) is None
