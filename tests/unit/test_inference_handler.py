import pytest
from unittest.mock import patch, MagicMock
from handlers.inference import main

@patch("handlers.inference.logger")  # Patch the logger directly in your module
@patch("app.helpers.environment.env")
def test_main(mock_env, mock_logger):
    # Mock the environment
    mock_env.return_value.APP_ENVIRONMENT = "local"

    # Call the main function
    result = main()

    # Print actual calls for debugging
    print("Actual calls:", mock_logger.info.call_args_list)

    # Assertions using f-string format to match exactly what the code produces
    mock_logger.info.assert_any_call(f"Currently in {mock_env.return_value.APP_ENVIRONMENT} environment")
    mock_logger.info.assert_any_call("Hello, from Spartan")
    assert result == {"status_code": 200}
