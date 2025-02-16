from unittest.mock import patch, MagicMock

import pytest

from app.helpers.tracer.factory import TracerFactory, get_tracer
from app.helpers.tracer.local import LocalTracer
from app.helpers.tracer.cloud import CloudTracer


def test_create_tracer_local():
    with patch("app.helpers.tracer.factory.os.getenv", return_value="local"):
        tracer = TracerFactory.create_tracer("test_service")
        assert isinstance(tracer, LocalTracer)
        assert tracer.service_name == "test_service"


def test_create_tracer_cloud():
    with patch("app.helpers.tracer.factory.os.getenv", side_effect=["cloud", "test_service"]):
        with patch("app.helpers.tracer.cloud.Tracer") as MockTracer:
            mock_tracer_instance = MagicMock()
            MockTracer.return_value = mock_tracer_instance
            mock_tracer_instance.service = "test_service"
            tracer = TracerFactory.create_tracer()
            assert isinstance(tracer, CloudTracer)
            assert tracer.tracer.service == "test_service"


def test_get_tracer_local():
    with patch("app.helpers.tracer.factory.os.getenv", return_value="local"):
        tracer = get_tracer("test_service")
        assert isinstance(tracer, LocalTracer)
        assert tracer.service_name == "test_service"


def test_get_tracer_cloud():
    with patch("app.helpers.tracer.factory.os.getenv", side_effect=["cloud", "test_service"]):
        with patch("app.helpers.tracer.cloud.Tracer") as MockTracer:
            mock_tracer_instance = MagicMock()
            MockTracer.return_value = mock_tracer_instance
            mock_tracer_instance.service = "test_service"
            tracer = get_tracer()
            assert isinstance(tracer, CloudTracer)
            assert tracer.tracer.service == "test_service"
