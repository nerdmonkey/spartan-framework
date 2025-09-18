"""
Unit Test Configuration - Uses mocked dependencies for isolation with pytest-mock
"""

import os

import pytest


@pytest.fixture(scope="function", autouse=True)
def mock_aws_services(mocker):
    """Mock AWS services for unit tests."""
    os.environ["APP_ENVIRONMENT"] = "test"

    mock_ddb = mocker.patch("app.helpers.ddb.dynamodb_client")
    mock_table = mocker.patch("app.helpers.ddb.table")
    mocker.patch("boto3.client")
    mocker.patch("boto3.resource")

    mock_table.return_value = mocker.Mock()
    mock_ddb.return_value = mocker.Mock()

    return {"dynamodb": mock_ddb, "table": mock_table}
