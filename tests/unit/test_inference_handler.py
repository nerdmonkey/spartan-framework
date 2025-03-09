from unittest.mock import patch, MagicMock

from handlers.inference import main


@patch("handlers.inference.logger")
@patch("handlers.inference.env")  # Change the patch path to match where env is imported
def test_main(mock_env, mock_logger):
    # Create a mock environment with the correct structure
    mock_env_instance = MagicMock()
    mock_env_instance.APP_ENVIRONMENT = "local"
    mock_env.return_value = mock_env_instance

    # Print debug information
    print("Mock env value:", mock_env_instance.APP_ENVIRONMENT)

    # Call the main function
    result = main()

    # Print actual calls for debugging
    print("Actual calls:", mock_logger.info.call_args_list)

    # Check the calls in order
    calls = [args[0] for args, _ in mock_logger.info.call_args_list]
    print("Actual log messages:", calls)

    assert calls == [
        "Currently in local environment",
        "Hello, from Spartan"
    ]

    # Check the return value
    assert result == {"status_code": 200}
