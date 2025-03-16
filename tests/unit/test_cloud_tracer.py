import sys
from unittest.mock import MagicMock, patch

import pytest

# Set up mocks before any imports
mock_xray_recorder = MagicMock()
mock_xray_core = MagicMock()
mock_xray_core.xray_recorder = mock_xray_recorder
mock_xray_sdk = MagicMock()
mock_xray_sdk.core = mock_xray_core

# Mock the modules
sys.modules["aws_xray_sdk"] = mock_xray_sdk
sys.modules["aws_xray_sdk.core"] = mock_xray_core
sys.modules["aws_xray_sdk.core.xray_recorder"] = mock_xray_recorder

# Now we can safely import CloudTracer
from app.helpers.tracer.cloud import CloudTracer


@pytest.fixture
def tracer():
    mock_recorder = MagicMock()
    mock_recorder.put_annotation = lambda key, value: None
    mock_recorder.begin_segment = lambda name: None
    mock_recorder.end_segment = lambda: None
    mock_recorder.begin_subsegment = lambda name: None
    mock_recorder.end_subsegment = lambda: None
    mock_recorder.context_manager.context.return_value = mock_recorder

    with patch("app.helpers.tracer.cloud.xray_recorder", mock_recorder):
        return CloudTracer(service_name="test_service")


def test_capture_lambda_handler(tracer):
    @tracer.capture_lambda_handler
    def handler(event, context):
        return "result"

    event = {"key": "value"}
    context = {}

    with patch.object(tracer.tracer, "put_annotation") as mock_put_annotation:
        result = handler(event, context)
        assert result == "result"
        assert mock_put_annotation.call_count == 2


def test_capture_method(tracer):
    class TestClass:
        @tracer.capture_method
        def method(self):
            return "result"

    test_instance = TestClass()

    with patch.object(tracer.tracer, "put_annotation") as mock_put_annotation:
        result = test_instance.method()
        assert result == "result"
        assert mock_put_annotation.call_count == 2


def test_create_segment(tracer):
    with patch.object(
        tracer.tracer, "begin_segment"
    ) as mock_begin_segment, patch.object(
        tracer.tracer, "end_segment"
    ) as mock_end_segment:
        with tracer.create_segment("test_segment"):
            pass
        mock_begin_segment.assert_called_once_with("test_segment")
        mock_end_segment.assert_called_once()


def test_create_subsegment(tracer):
    with patch.object(
        tracer.tracer, "begin_subsegment"
    ) as mock_begin_subsegment, patch.object(
        tracer.tracer, "end_subsegment"
    ) as mock_end_subsegment:
        with tracer.create_subsegment("test_subsegment"):
            pass
        mock_begin_subsegment.assert_called_once_with("test_subsegment")
        mock_end_subsegment.assert_called_once()


def test_put_annotation(tracer):
    with patch.object(tracer.tracer, "put_annotation") as mock_put_annotation:
        tracer.put_annotation("test_key", "test_value")
        mock_put_annotation.assert_called_once_with("test_key", "test_value")


def test_context_missing(tracer):
    mock_recorder = MagicMock()
    mock_recorder.context_manager.context.return_value = None

    with patch("app.helpers.tracer.cloud.xray_recorder", mock_recorder):
        tracer = CloudTracer(service_name="test_service")
        # Should not raise an error when context is missing
        tracer.put_annotation("test_key", "test_value")
