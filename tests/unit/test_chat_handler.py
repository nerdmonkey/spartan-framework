import json
from unittest.mock import Mock, patch

import pytest

from app.helpers.context import MockLambdaContext
from handlers.chat import main


@pytest.fixture
def lambda_context():
    return MockLambdaContext()


@pytest.fixture
def mock_azure_chat():
    with patch("handlers.chat.AzureChatOpenAI") as mock:
        mock_instance = Mock()
        mock_instance.invoke.return_value = "Test response"
        mock.return_value = mock_instance
        yield mock


@pytest.fixture
def mock_env():
    env_values = {
        "AZURE_OPENAI_API_KEY": "test-key",
        "AZURE_OPENAI_ENDPOINT": "test-endpoint",
        "AZURE_OPENAI_DEPLOYMENT_NAME": "test-deployment",
        "AZURE_OPENAI_API_VERSION": "test-version",
    }
    with patch("handlers.chat.env", side_effect=lambda x: env_values.get(x)):
        yield env_values


def test_successful_chat_response(lambda_context, mock_azure_chat, mock_env):
    # Arrange
    test_prompt = "What is AI?"
    event = {"prompt": json.dumps({"text": test_prompt})}

    # Act
    response = main(event, lambda_context)

    # Assert
    assert response["statusCode"] == 200
    assert response["headers"]["Content-Type"] == "application/json"
    assert response["headers"]["Access-Control-Allow-Origin"] == "*"

    body = json.loads(response["body"])
    assert "message" in body
    assert body["message"] == "Test response"

    # Verify Azure Chat was called correctly
    mock_azure_chat.assert_called_once_with(
        openai_api_key=mock_env["AZURE_OPENAI_API_KEY"],
        azure_endpoint=mock_env["AZURE_OPENAI_ENDPOINT"],
        deployment_name=mock_env["AZURE_OPENAI_DEPLOYMENT_NAME"],
        api_version=mock_env["AZURE_OPENAI_API_VERSION"],
        temperature=0,
    )


def test_empty_prompt(lambda_context, mock_azure_chat, mock_env):
    # Test with empty prompt
    event = {"prompt": json.dumps({})}
    response = main(event, lambda_context)

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert "message" in body

    # Verify default "Hello World" was used
    mock_azure_chat.return_value.invoke.assert_called_once_with("Hello World")


def test_missing_prompt(lambda_context, mock_azure_chat, mock_env):
    # Test with no prompt in event
    event = {}
    response = main(event, lambda_context)

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert "message" in body

    # Verify default "Hello World" was used
    mock_azure_chat.return_value.invoke.assert_called_once_with("Hello World")


def test_azure_api_error(lambda_context, mock_azure_chat, mock_env):
    # Arrange
    mock_azure_chat.return_value.invoke.side_effect = Exception(
        "Azure API Error"
    )
    event = {"prompt": json.dumps({"text": "Test prompt"})}

    # Act
    response = main(event, lambda_context)

    # Assert
    assert response["statusCode"] == 500
    assert response["headers"]["Content-Type"] == "application/json"
    body = json.loads(response["body"])
    assert "error" in body
    assert body["error"] == "Azure API Error"


def test_invalid_json_prompt(lambda_context, mock_azure_chat, mock_env):
    # Test with invalid JSON in prompt
    event = {"prompt": "invalid json"}
    response = main(event, lambda_context)

    assert response["statusCode"] == 500
    body = json.loads(response["body"])
    assert "error" in body


@pytest.fixture(autouse=True)
def setup_and_teardown():
    # Setup - runs before each test
    yield
    # Teardown - runs after each test
