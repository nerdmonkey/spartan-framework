"""
Unit tests for app/helpers/ddb.py DynamoDB helper functions.
Tests get_dynamodb_clients with different environments (local, lambda, container)
and error handling scenarios.
"""

from types import SimpleNamespace

import pytest
from botocore.exceptions import ClientError

import app.helpers.ddb as ddb_mod


@pytest.fixture(autouse=True)
def reset_ddb_globals():
    """Reset global DynamoDB client variables before each test."""
    ddb_mod.dynamodb_resource = None
    ddb_mod.dynamodb_client = None
    ddb_mod.table = None
    ddb_mod.table_name = None
    try:
        ddb_mod.get_dynamodb_clients.cache_clear()
    except Exception:
        pass
    yield


def test_get_dynamodb_clients_local_environment(mocker):
    """Test DynamoDB client initialization for local environment."""
    settings = SimpleNamespace(
        DDB_TYPE="local",
        DDB_TABLE_NAME="local_table",
        APP_RUNTIME="lambda",
        DDB_MAX_POOL_CONNECTIONS=5,
        DDB_MAX_RETRY_ATTEMPTS=2,
        DDB_READ_TIMEOUT=30,
        DDB_CONNECT_TIMEOUT=5,
        DDB_REGION="us-east-1",
    )
    mocker.patch("app.helpers.ddb.env", return_value=settings)

    fake_table = SimpleNamespace(name="local_table")
    fake_resource = SimpleNamespace(Table=lambda name: fake_table)
    fake_client = SimpleNamespace(
        describe_table=lambda TableName: {"Table": {"TableStatus": "ACTIVE"}}
    )

    mock_resource = mocker.patch(
        "app.helpers.ddb.boto3.resource", return_value=fake_resource
    )
    mock_client = mocker.patch("app.helpers.ddb.boto3.client", return_value=fake_client)
    mock_logger = mocker.patch("app.helpers.ddb.logger")

    resource, client, table = ddb_mod.get_dynamodb_clients()

    assert resource is fake_resource
    assert client is fake_client
    assert table is fake_table

    # Verify local endpoint URL was used
    assert "endpoint_url" in mock_resource.call_args.kwargs
    assert mock_resource.call_args.kwargs["endpoint_url"] == "http://localhost:8000"
    assert "endpoint_url" in mock_client.call_args.kwargs

    # Verify logging
    mock_logger.info.assert_any_call("DynamoDB connected - Status: ACTIVE")
    mock_logger.info.assert_any_call("Initialized LOCAL DynamoDB clients")


def test_get_dynamodb_clients_lambda_environment(mocker):
    """Test DynamoDB client initialization for Lambda environment."""
    settings = SimpleNamespace(
        DDB_TYPE="cloud",
        DDB_TABLE_NAME="lambda_table",
        APP_RUNTIME="lambda",
        DDB_MAX_POOL_CONNECTIONS=20,
        DDB_MAX_RETRY_ATTEMPTS=3,
        DDB_READ_TIMEOUT=60,
        DDB_CONNECT_TIMEOUT=10,
        DDB_REGION="us-west-2",
    )
    mocker.patch("app.helpers.ddb.env", return_value=settings)

    fake_table = SimpleNamespace(name="lambda_table")
    fake_resource = SimpleNamespace(Table=lambda name: fake_table)
    fake_client = SimpleNamespace(
        describe_table=lambda TableName: {"Table": {"TableStatus": "ACTIVE"}}
    )

    mock_resource = mocker.patch(
        "app.helpers.ddb.boto3.resource", return_value=fake_resource
    )
    mock_client = mocker.patch("app.helpers.ddb.boto3.client", return_value=fake_client)
    mock_logger = mocker.patch("app.helpers.ddb.logger")

    resource, client, table = ddb_mod.get_dynamodb_clients()

    assert resource is fake_resource
    assert client is fake_client
    assert table is fake_table

    # Verify no endpoint_url for cloud
    assert "endpoint_url" not in mock_resource.call_args.kwargs
    assert "endpoint_url" not in mock_client.call_args.kwargs

    # Verify config has correct max_pool_connections (capped at 10 for Lambda)
    config = mock_resource.call_args.kwargs["config"]
    assert config.max_pool_connections == 10  # min(20, 10) for Lambda

    # Verify logging
    mock_logger.info.assert_any_call("Initialized LAMBDA DynamoDB clients")


def test_get_dynamodb_clients_container_environment(mocker):
    """Test DynamoDB client initialization for container environment."""
    settings = SimpleNamespace(
        DDB_TYPE="cloud",
        DDB_TABLE_NAME="container_table",
        APP_RUNTIME="container",
        DDB_MAX_POOL_CONNECTIONS=50,
        DDB_MAX_RETRY_ATTEMPTS=5,
        DDB_READ_TIMEOUT=120,
        DDB_CONNECT_TIMEOUT=15,
        DDB_REGION="eu-west-1",
    )
    mocker.patch("app.helpers.ddb.env", return_value=settings)

    fake_table = SimpleNamespace(name="container_table")
    fake_resource = SimpleNamespace(Table=lambda name: fake_table)
    fake_client = SimpleNamespace(
        describe_table=lambda TableName: {"Table": {"TableStatus": "ACTIVE"}}
    )

    mock_resource = mocker.patch(
        "app.helpers.ddb.boto3.resource", return_value=fake_resource
    )
    mocker.patch("app.helpers.ddb.boto3.client", return_value=fake_client)
    mock_logger = mocker.patch("app.helpers.ddb.logger")

    resource, client, table = ddb_mod.get_dynamodb_clients()

    assert resource is fake_resource

    # Verify config uses full max_pool_connections for container (no cap)
    config = mock_resource.call_args.kwargs["config"]
    assert config.max_pool_connections == 50  # Full value for container

    # Verify logging
    mock_logger.info.assert_any_call("Initialized CONTAINER DynamoDB clients")


def test_get_dynamodb_clients_table_not_found(mocker):
    """Test DynamoDB client initialization when table doesn't exist."""
    settings = SimpleNamespace(
        DDB_TYPE="local",
        DDB_TABLE_NAME="missing_table",
        APP_RUNTIME="lambda",
        DDB_MAX_POOL_CONNECTIONS=5,
        DDB_MAX_RETRY_ATTEMPTS=2,
        DDB_READ_TIMEOUT=30,
        DDB_CONNECT_TIMEOUT=5,
        DDB_REGION="us-east-1",
    )
    mocker.patch("app.helpers.ddb.env", return_value=settings)

    fake_table = SimpleNamespace(name="missing_table")
    fake_resource = SimpleNamespace(Table=lambda name: fake_table)

    # Simulate ResourceNotFoundException
    def describe_table_not_found(TableName):
        error_response = {
            "Error": {"Code": "ResourceNotFoundException", "Message": "Table not found"}
        }
        raise ClientError(error_response, "DescribeTable")

    fake_client = SimpleNamespace(describe_table=describe_table_not_found)

    mocker.patch("app.helpers.ddb.boto3.resource", return_value=fake_resource)
    mocker.patch("app.helpers.ddb.boto3.client", return_value=fake_client)
    mock_logger = mocker.patch("app.helpers.ddb.logger")

    resource, client, table = ddb_mod.get_dynamodb_clients()

    # Should still return clients despite table not found
    assert resource is fake_resource
    assert client is fake_client
    assert table is fake_table

    # Verify warning was logged
    mock_logger.warning.assert_called_once_with("Table 'missing_table' not found")


def test_get_dynamodb_clients_describe_table_error(mocker):
    """
    Test DynamoDB client initialization with
    describe_table error (non-ResourceNotFound).
    """
    settings = SimpleNamespace(
        DDB_TYPE="local",
        DDB_TABLE_NAME="error_table",
        APP_RUNTIME="lambda",
        DDB_MAX_POOL_CONNECTIONS=5,
        DDB_MAX_RETRY_ATTEMPTS=2,
        DDB_READ_TIMEOUT=30,
        DDB_CONNECT_TIMEOUT=5,
        DDB_REGION="us-east-1",
    )
    mocker.patch("app.helpers.ddb.env", return_value=settings)

    fake_table = SimpleNamespace(name="error_table")
    fake_resource = SimpleNamespace(Table=lambda name: fake_table)

    # Simulate AccessDeniedException (not ResourceNotFoundException)
    def describe_table_access_denied(TableName):
        error_response = {
            "Error": {"Code": "AccessDeniedException", "Message": "Access denied"}
        }
        raise ClientError(error_response, "DescribeTable")

    fake_client = SimpleNamespace(describe_table=describe_table_access_denied)

    mocker.patch("app.helpers.ddb.boto3.resource", return_value=fake_resource)
    mocker.patch("app.helpers.ddb.boto3.client", return_value=fake_client)
    mocker.patch("app.helpers.ddb.logger")

    # Should re-raise non-ResourceNotFoundException errors
    with pytest.raises(ClientError) as exc_info:
        ddb_mod.get_dynamodb_clients()

    assert exc_info.value.response["Error"]["Code"] == "AccessDeniedException"


def test_get_dynamodb_clients_connection_error(mocker):
    """Test DynamoDB client initialization with connection error."""
    settings = SimpleNamespace(
        DDB_TYPE="local",
        DDB_TABLE_NAME="conn_error_table",
        APP_RUNTIME="lambda",
        DDB_MAX_POOL_CONNECTIONS=5,
        DDB_MAX_RETRY_ATTEMPTS=2,
        DDB_READ_TIMEOUT=30,
        DDB_CONNECT_TIMEOUT=5,
        DDB_REGION="us-east-1",
    )
    mocker.patch("app.helpers.ddb.env", return_value=settings)

    # Simulate connection error during resource creation
    mocker.patch(
        "app.helpers.ddb.boto3.resource", side_effect=Exception("Connection failed")
    )
    mock_logger = mocker.patch("app.helpers.ddb.logger")

    with pytest.raises(Exception) as exc_info:
        ddb_mod.get_dynamodb_clients()

    assert str(exc_info.value) == "Connection failed"
    mock_logger.error.assert_called_once()
    assert "Failed to initialize DynamoDB clients" in mock_logger.error.call_args[0][0]


def test_get_clients_lazy_initialization(mocker):
    """Test get_clients() lazy initialization."""
    settings = SimpleNamespace(
        DDB_TYPE="local",
        DDB_TABLE_NAME="lazy_table",
        APP_RUNTIME="lambda",
        DDB_MAX_POOL_CONNECTIONS=5,
        DDB_MAX_RETRY_ATTEMPTS=2,
        DDB_READ_TIMEOUT=30,
        DDB_CONNECT_TIMEOUT=5,
        DDB_REGION="us-east-1",
    )
    mocker.patch("app.helpers.ddb.env", return_value=settings)

    fake_table = SimpleNamespace(name="lazy_table")
    fake_resource = SimpleNamespace(Table=lambda name: fake_table)
    fake_client = SimpleNamespace(
        describe_table=lambda TableName: {"Table": {"TableStatus": "ACTIVE"}}
    )

    mocker.patch("app.helpers.ddb.boto3.resource", return_value=fake_resource)
    mocker.patch("app.helpers.ddb.boto3.client", return_value=fake_client)

    # Verify globals are None before first call
    assert ddb_mod.dynamodb_resource is None
    assert ddb_mod.dynamodb_client is None
    assert ddb_mod.table is None
    assert ddb_mod.table_name is None

    # First call initializes
    resource, client, table = ddb_mod.get_clients()
    assert resource is fake_resource
    assert client is fake_client
    assert table is fake_table

    # Verify globals are set
    assert ddb_mod.dynamodb_resource is fake_resource
    assert ddb_mod.dynamodb_client is fake_client
    assert ddb_mod.table is fake_table
    assert ddb_mod.table_name == "lazy_table"

    # Second call returns cached values
    resource2, client2, table2 = ddb_mod.get_clients()
    assert resource2 is fake_resource
    assert client2 is fake_client
    assert table2 is fake_table
