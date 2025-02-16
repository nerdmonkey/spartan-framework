import json
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from app.helpers.tracer.local import LocalTracer


@pytest.fixture
def tracer():
    with patch.object(
        LocalTracer,
        "_get_trace_file_path",
        return_value=Path(__file__).parent.parent.parent.parent
        / "storage"
        / "traces"
        / "spartan.trace",
    ):
        return LocalTracer(service_name="test_service")


def test_trace_file_path(tracer):
    expected_path = (
        Path(__file__).parent.parent.parent.parent
        / "storage"
        / "traces"
        / "spartan.trace"
    )
    assert tracer.trace_file == expected_path


def test_ensure_trace_directory_exists(tracer):
    with patch("pathlib.Path.mkdir") as mock_mkdir:
        tracer._ensure_trace_directory_exists()
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)


def test_write_trace(tracer):
    trace_entry = {
        "timestamp": "2023-01-01 00:00:00",
        "service": "test_service",
        "segment": "test_segment",
        "metadata": {"key": "value"},
    }
    trace_message = json.dumps(trace_entry, default=str)

    with patch("builtins.open", mock_open()) as mock_file, patch(
        "app.helpers.tracer.local.datetime"
    ) as mock_datetime:
        mock_datetime.now.return_value.strftime.return_value = (
            "2023-01-01 00:00:00"
        )
        tracer._write_trace("test_segment", {"key": "value"})
        mock_file().write.assert_called_once_with(trace_message + "\n")


def test_capture_lambda_handler(tracer):
    @tracer.capture_lambda_handler
    def handler(event, context):
        return "result"

    event = {"key": "value"}
    context = {}

    with patch.object(tracer, "_write_trace") as mock_write_trace:
        result = handler(event, context)
        assert result == "result"
        assert mock_write_trace.call_count == 2


def test_capture_method(tracer):
    class TestClass:
        @tracer.capture_method
        def method(self):
            return "result"

    test_instance = TestClass()

    with patch.object(tracer, "_write_trace") as mock_write_trace:
        result = test_instance.method()
        assert result == "result"
        assert mock_write_trace.call_count == 2


def test_create_segment(tracer):
    with patch.object(tracer, "_write_trace") as mock_write_trace:
        with tracer.create_segment("test_segment"):
            pass
        assert mock_write_trace.call_count == 2
