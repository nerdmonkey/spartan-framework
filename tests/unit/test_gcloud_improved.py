"""
Unit tests for the improved GCloudLogger implementation.
Tests the GCP best practices version with structured logging.
"""

from unittest.mock import MagicMock, patch


def test_gcloud_logger_basic_initialization(monkeypatch):
    """Test that GCloudLogger initializes correctly with GCP client."""
    # Mock GCP client
    mock_client = MagicMock()
    mock_logger = MagicMock()
    mock_client.logger.return_value = mock_logger

    with patch(
        "app.services.logging.gcloud.get_gcp_logging_client", return_value=mock_client
    ):
        from app.services.logging.gcloud import GCloudLogger

        logger = GCloudLogger("test-service", level="INFO", sample_rate=1.0)

        assert logger.service_name == "test-service"
        assert logger.level == "INFO"
        assert logger.sample_rate == 1.0
        assert logger.use_gcp is True
        mock_client.logger.assert_called_once_with("test-service")


def test_gcloud_logger_fallback_when_client_unavailable(monkeypatch):
    """Test fallback to print when GCP client is unavailable."""
    with patch("app.services.logging.gcloud.get_gcp_logging_client", return_value=None):
        from app.services.logging.gcloud import GCloudLogger

        logger = GCloudLogger("test-service")

        assert logger.use_gcp is False
        assert logger.logger is None


def test_gcloud_logger_info_with_structured_data(monkeypatch):
    """Test that info() creates structured logs with user data."""
    mock_client = MagicMock()
    mock_logger = MagicMock()
    mock_client.logger.return_value = mock_logger

    with patch(
        "app.services.logging.gcloud.get_gcp_logging_client", return_value=mock_client
    ):
        from app.services.logging.gcloud import GCloudLogger

        logger = GCloudLogger("test-service", sample_rate=1.0)
        logger.info("Test message", extra={"user_id": "123", "action": "login"})

        # Verify log_struct was called
        assert mock_logger.log_struct.called
        call_args = mock_logger.log_struct.call_args

        # Check json_payload contains our data
        json_payload = call_args[0][0]
        assert json_payload["message"] == "Test message"
        assert json_payload["user_id"] == "123"
        assert json_payload["action"] == "login"
        assert json_payload["service"] == "test-service"

        # Check severity is passed correctly
        assert call_args[1]["severity"] == "INFO"


def test_gcloud_logger_pii_sanitization(monkeypatch):
    """Test that sensitive fields are redacted."""
    mock_client = MagicMock()
    mock_logger = MagicMock()
    mock_client.logger.return_value = mock_logger

    with patch(
        "app.services.logging.gcloud.get_gcp_logging_client", return_value=mock_client
    ):
        from app.services.logging.gcloud import GCloudLogger

        logger = GCloudLogger("test-service", sample_rate=1.0)
        logger.info(
            "Test",
            extra={"password": "secret123", "token": "abc", "safe_field": "visible"},
        )

        json_payload = mock_logger.log_struct.call_args[0][0]
        assert json_payload["password"] == "[REDACTED]"
        assert json_payload["token"] == "[REDACTED]"
        assert json_payload["safe_field"] == "visible"


def test_gcloud_logger_sampling(monkeypatch):
    """Test that sampling works correctly."""
    mock_client = MagicMock()
    mock_logger = MagicMock()
    mock_client.logger.return_value = mock_logger

    with patch(
        "app.services.logging.gcloud.get_gcp_logging_client", return_value=mock_client
    ):
        from app.services.logging.gcloud import GCloudLogger

        # Test 0% sampling - nothing should be logged
        logger = GCloudLogger("test-service", sample_rate=0.0)
        logger.info("Should not log")

        assert not mock_logger.log_struct.called

        # Test 100% sampling - should log
        mock_logger.reset_mock()
        logger = GCloudLogger("test-service", sample_rate=1.0)
        logger.info("Should log")

        assert mock_logger.log_struct.called


def test_gcloud_logger_resource_labels_cloud_run(monkeypatch):
    """Test that Cloud Run resource labels are detected."""
    mock_client = MagicMock()
    mock_logger = MagicMock()
    mock_client.logger.return_value = mock_logger

    # Mock Resource class to track initialization
    mock_resource_instance = MagicMock()
    mock_resource_class = MagicMock(return_value=mock_resource_instance)

    # Mock env() to return Cloud Run environment values
    def mock_env(key, default=None):
        env_values = {
            "K_SERVICE": "my-service",
            "K_REVISION": "my-service-abc123",
            "K_CONFIGURATION": "my-config",
        }
        return env_values.get(key, default)

    with patch(
        "app.services.logging.gcloud.get_gcp_logging_client", return_value=mock_client
    ), patch("app.services.logging.gcloud.env", side_effect=mock_env), patch(
        "app.services.logging.gcloud.Resource", mock_resource_class
    ):
        from app.services.logging.gcloud import GCloudLogger

        logger = GCloudLogger("test-service", sample_rate=1.0)

        assert logger.resource is not None
        # Verify Resource was called with correct arguments
        mock_resource_class.assert_called_once()
        call_kwargs = mock_resource_class.call_args[1]
        assert call_kwargs["type"] == "cloud_run_revision"
        assert call_kwargs["labels"]["service_name"] == "my-service"
        assert call_kwargs["labels"]["revision_name"] == "my-service-abc123"


def test_gcloud_logger_exception_with_context(monkeypatch):
    """Test that exception() captures exception details."""
    mock_client = MagicMock()
    mock_logger = MagicMock()
    mock_client.logger.return_value = mock_logger

    with patch(
        "app.services.logging.gcloud.get_gcp_logging_client", return_value=mock_client
    ):
        from app.services.logging.gcloud import GCloudLogger

        logger = GCloudLogger("test-service", sample_rate=1.0)

        try:
            raise ValueError("Test error")
        except ValueError:
            logger.exception("An error occurred", extra={"context": "test"})

        assert mock_logger.log_struct.called
        json_payload = mock_logger.log_struct.call_args[0][0]

        # Check exception details are included
        assert "exception" in json_payload
        assert json_payload["exception"]["type"] == "ValueError"
        assert json_payload["exception"]["message"] == "Test error"
        assert json_payload["context"] == "test"


def test_gcloud_logger_source_location(monkeypatch):
    """Test that source location is captured."""
    mock_client = MagicMock()
    mock_logger = MagicMock()
    mock_client.logger.return_value = mock_logger

    with patch(
        "app.services.logging.gcloud.get_gcp_logging_client", return_value=mock_client
    ):
        from app.services.logging.gcloud import GCloudLogger

        logger = GCloudLogger("test-service", sample_rate=1.0)
        logger.info("Test")

        call_kwargs = mock_logger.log_struct.call_args[1]

        # Source location should be included
        assert "source_location" in call_kwargs
        source_loc = call_kwargs["source_location"]
        assert "file" in source_loc
        assert "line" in source_loc
        assert "function" in source_loc


def test_gcloud_logger_all_severity_levels(monkeypatch):
    """Test all logging methods work with correct severity."""
    mock_client = MagicMock()
    mock_logger = MagicMock()
    mock_client.logger.return_value = mock_logger

    with patch(
        "app.services.logging.gcloud.get_gcp_logging_client", return_value=mock_client
    ):
        from app.services.logging.gcloud import GCloudLogger

        logger = GCloudLogger("test-service", sample_rate=1.0)

        # Test all methods
        logger.debug("Debug message")
        assert mock_logger.log_struct.call_args[1]["severity"] == "DEBUG"

        logger.info("Info message")
        assert mock_logger.log_struct.call_args[1]["severity"] == "INFO"

        logger.warning("Warning message")
        assert mock_logger.log_struct.call_args[1]["severity"] == "WARNING"

        logger.error("Error message")
        assert mock_logger.log_struct.call_args[1]["severity"] == "ERROR"

        logger.critical("Critical message")
        assert mock_logger.log_struct.call_args[1]["severity"] == "CRITICAL"


def test_gcloud_logger_fallback_prints_json(monkeypatch, capsys):
    """Test that fallback mode prints JSON for local development."""
    with patch("app.services.logging.gcloud.get_gcp_logging_client", return_value=None):
        from app.services.logging.gcloud import GCloudLogger

        logger = GCloudLogger("test-service", sample_rate=1.0)
        logger.info("Test message", extra={"user": "123"})

        captured = capsys.readouterr()
        # Should print JSON output
        assert "Test message" in captured.out
        assert '"user": "123"' in captured.out
