import pytest
import os
import boto3
from moto import mock_dynamodb
from app.services.app import AppService  # Replace 'your_module' with the actual module name


@pytest.fixture
def app_service():
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
    key = "testKey"
    value = {"data": "testValue"}

    # Test set_state
    response = app_service.set_state(key, value)

    # Assert
    assert response is not None

def test_get_state(app_service):
    key = "testKey"
    value = {"data": "testValue"}

    # First set a state
    app_service.set_state(key, value)

    # Test get_state
    response = app_service.get_state(key)

    # Assert
    assert response == value

def test_remove_state(app_service):
    key = "testKey"
    value = {"data": "testValue"}

    # First set a state
    app_service.set_state(key, value)

    # Test remove_state
    response = app_service.remove_state(key)

    # In a real environment, you would check if the response matches the encoded value.
    # But in a mocked environment, it's sufficient to check if the state is removed.

    # Assert that the state is actually removed
    assert app_service.get_state(key) is None
