from unittest.mock import MagicMock, patch


def test_main_function_logs_event():
    """Test that main function logs the cloud event with extra data."""
    # Create a mock cloud event
    mock_event = MagicMock()
    mock_event.__getitem__.side_effect = lambda key: {
        "id": "test-event-123",
        "type": "google.cloud.pubsub.topic.v1.messagePublished",
        "source": "//pubsub.googleapis.com/projects/test/topics/test-topic",
    }[key]
    mock_event.data = {"message": "test message"}

    with patch("main.logger") as mock_logger, patch("main.env") as mock_env:
        mock_env.side_effect = lambda key, default=None: {
            "APP_ENVIRONMENT": "test",
            "LOG_LEVEL": "INFO",
            "LOG_CHANNEL": "gcloud",
        }.get(key, default)

        # Import here to avoid execution at module level
        from main import main

        main(mock_event)
        mock_logger.info.assert_called_once()
        # Verify the call includes message and extra data
        call_args, call_kwargs = mock_logger.info.call_args
        assert call_args[0] == "Received Cloud Event"
        assert "extra" in call_kwargs
        expected_event_type = "google.cloud.pubsub.topic.v1.messagePublished"
        assert call_kwargs["extra"]["event_type"] == expected_event_type
        assert call_kwargs["extra"]["event_id"] == "test-event-123"
