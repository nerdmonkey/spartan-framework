import sys
import types
from unittest.mock import MagicMock, patch

import pytest

import handlers.inference as inference_module


def test_main_logs_and_returns(mocker):
    # Arrange
    event = {"foo": "bar"}

    class DummyContext:
        def __init__(self):
            self.value = 123

    context = DummyContext()
    logger_mock = mocker.patch.object(inference_module, "logger")

    # Act
    result = inference_module.main(event, context)

    # Assert
    logger_mock.info.assert_any_call(
        f"Event: {event}, Context: {getattr(context, '__dict__', str(context))}"
    )
    logger_mock.info.assert_any_call("This is an info message")
    logger_mock.debug.assert_called_with("This is a debug message")
    logger_mock.error.assert_called_with(
        "This is an error message",
        extra={"error_code": 500, "details": "An error occurred"},
    )
    logger_mock.warning.assert_called_with("This is a warning message")
    assert result == {"statusCode": 200, "body": "Hello Spartan!"}


def test_main_exception_logging(mocker):
    # Patch logger
    logger_mock = mocker.patch.object(inference_module, "logger")
    # Patch MockLambdaEvent and MockLambdaContext to raise error in main
    mocker.patch("handlers.inference.main", side_effect=Exception("fail"))
    mocker.patch("builtins.print")  # Suppress print

    # Patch sys.modules to inject mocks for app.helpers.context
    mock_context_mod = types.ModuleType("app.helpers.context")
    mock_context_mod.MockLambdaEvent = MagicMock(return_value="event")
    mock_context_mod.MockLambdaContext = MagicMock(return_value="context")
    sys.modules["app.helpers.context"] = mock_context_mod

    # Simulate __main__ block
    with patch.object(inference_module, "__name__", "__main__"):
        try:
            exec(
                "from handlers.inference import main\n"
                "from app.helpers.context import MockLambdaContext, MockLambdaEvent\n"
                "event = MockLambdaEvent()\n"
                "context = MockLambdaContext()\n"
                "try:\n"
                "    print(main(event, context))\n"
                "except Exception as e:\n"
                "    logger.exception('Unhandled exception in main', extra={'error': str(e)})\n",
                {"logger": logger_mock, "main": inference_module.main},
            )
        except Exception:
            pass
    logger_mock.exception.assert_called_with(
        "Unhandled exception in main", extra={"error": "fail"}
    )


def test_main_with_realistic_context(mocker):
    # Arrange
    event = {"foo": "bar"}

    class DummyContext:
        def __init__(self):
            self.value = 42

    context = DummyContext()
    logger_mock = mocker.patch.object(inference_module, "logger")

    # Act
    result = inference_module.main(event, context)

    # Assert
    logger_mock.info.assert_any_call(
        f"Event: {event}, Context: {getattr(context, '__dict__', str(context))}"
    )
    assert result["statusCode"] == 200
    assert "Spartan" in result["body"]
