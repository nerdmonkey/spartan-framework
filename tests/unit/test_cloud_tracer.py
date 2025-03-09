from unittest.mock import patch

import pytest

from app.helpers.tracer.cloud import CloudTracer


@pytest.fixture
def tracer():
    with patch("app.helpers.tracer.cloud.Tracer"):
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
        assert mock_put_annotation.call_count == 1


def test_capture_method(tracer):
    class TestClass:
        @tracer.capture_method
        def method(self):
            return "result"

    test_instance = TestClass()

    with patch.object(tracer.tracer, "put_annotation") as mock_put_annotation:
        result = test_instance.method()
        assert result == "result"
        assert mock_put_annotation.call_count == 1


def test_create_segment(tracer):
    with patch.object(
        tracer.tracer.provider, "in_subsegment"
    ) as mock_in_subsegment:
        with tracer.create_segment("test_segment"):
            pass
        assert mock_in_subsegment.call_count == 1
