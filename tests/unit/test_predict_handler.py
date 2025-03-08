from unittest.mock import MagicMock, patch

from handlers.predict import main


@patch("handlers.predict.get_logger")
@patch("handlers.predict.standard_logger")
def test_main(mock_standard_logger, mock_get_logger):
    # Arrange
    mock_logger = MagicMock()
    mock_get_logger.return_value = mock_logger
    event = {"key": "value"}
    context = {"context_key": "context_value"}

    # Act
    response = main(event, context)

    # Assert
    mock_logger.info.assert_any_call("Predicting...")
    mock_logger.info.assert_any_call(
        "Event", extra={"event": event, "context": context}
    )
    assert response == {"statusCode": 200, "body": "Hello World"}
