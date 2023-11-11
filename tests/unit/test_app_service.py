import os
from unittest.mock import patch

import boto3
import pytest
from moto import mock_dynamodb

from app.services.app import AppService


@pytest.fixture(scope="function")
def dynamodb_setup():
    """
    Fixture for setting up DynamoDB for testing.
    """
    os.environ["GSM_TABLE"] = "GlobalStateTable"
    os.environ["AWS_REGION"] = "us-east-1"

    with mock_dynamodb():
        dynamodb = boto3.resource("dynamodb", "us-east-1")
        table = dynamodb.create_table(
            TableName="GlobalStateTable",
            KeySchema=[{"AttributeName": "Key", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "Key", "AttributeType": "S"}],
            ProvisionedThroughput={"ReadCapacityUnits": 10, "WriteCapacityUnits": 10},
        )
        table.meta.client.get_waiter("table_exists").wait(TableName="GlobalStateTable")
        yield


@pytest.fixture(scope="function")
def app_service(dynamodb_setup):
    """
    Fixture for creating an instance of AppService.
    """
    return AppService()


def test_set_state(app_service):
    """
    Test setting a state in the DynamoDB table.
    """
    key = "testKey"
    value = {"data": "testValue"}
    result = app_service.set_state(key, value)

    assert result is not None


def test_get_state(app_service):
    """
    Test retrieving a state from the DynamoDB table.
    """
    key = "testKey"
    value = {"data": "testValue"}
    app_service.set_state(key, value)

    result = app_service.get_state(key)
    assert result == value


def test_remove_state(app_service):
    """
    Test removing a state from the DynamoDB table.
    """
    # Mock delete_item method to include 'Attr_Data' in the response
    with patch.object(
        app_service.table,
        "delete_item",
        return_value={"Attributes": {"Attr_Data": "some_serialized_data"}},
    ):
        key = "testKey"
        value = {"data": "testValue"}
        app_service.set_state(key, value)

        result = app_service.remove_state(key)
        assert result == "some_serialized_data"
