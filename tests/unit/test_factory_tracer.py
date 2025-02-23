from unittest.mock import patch

import pytest

from app.helpers.tracer.cloud import CloudTracer
from app.helpers.tracer.factory import TracerFactory, get_tracer
from app.helpers.tracer.local import LocalTracer


@pytest.fixture
def mock_xray_recorder():
    """Mock AWS X-Ray recorder"""
    with patch("aws_xray_sdk.core.xray_recorder") as mock:
        yield mock


@pytest.fixture
def mock_env_local():
    with patch.dict(
        "os.environ", {"APP_ENVIRONMENT": "local", "APP_NAME": "test-service"}
    ):
        yield


@pytest.fixture
def mock_env_cloud():
    with patch.dict(
        "os.environ", {"APP_ENVIRONMENT": "cloud", "APP_NAME": "test-service"}
    ):
        yield


def test_create_tracer_local(mock_env_local):
    """Test creating local tracer"""
    tracer = TracerFactory.create_tracer("test-service")
    assert isinstance(tracer, LocalTracer)


def test_create_tracer_cloud(mock_env_cloud, mock_xray_recorder):
    """Test creating cloud tracer"""
    with patch("app.helpers.tracer.cloud.xray_recorder", mock_xray_recorder):
        tracer = TracerFactory.create_tracer("test-service")
        assert isinstance(tracer, CloudTracer)


def test_invalid_service_name_direct():
    """Test behavior with invalid service names passed directly"""
    invalid_names = [None, "", "  "]

    with patch.dict(
        "os.environ",
        {"APP_ENVIRONMENT": "local", "APP_NAME": ""},  # Set empty APP_NAME
    ):
        for name in invalid_names:
            with pytest.raises(ValueError) as exc_info:
                TracerFactory.create_tracer(name)
            assert str(exc_info.value) == "Invalid service name"


def test_invalid_service_name_from_env():
    """Test behavior with invalid service name from environment"""
    with patch.dict(
        "os.environ",
        {"APP_ENVIRONMENT": "local", "APP_NAME": ""},  # Set empty APP_NAME
    ):
        with pytest.raises(ValueError) as exc_info:
            TracerFactory.create_tracer()  # No service name provided, should fall back to APP_NAME
        assert str(exc_info.value) == "Invalid service name"


def test_default_service_name(mock_env_local):
    """Test default service name handling"""
    tracer = TracerFactory.create_tracer()
    assert isinstance(tracer, LocalTracer)
    # Verify it uses the APP_NAME from environment
    assert tracer.service_name == "test-service"


def test_tracer_singleton(mock_env_local):
    """Test tracer singleton pattern"""
    tracer1 = get_tracer("test-service")
    tracer2 = get_tracer("test-service")
    assert tracer1 is tracer2  # Should be the same instance


def test_different_service_tracers(mock_env_local):
    """Test different service names create different tracers"""
    tracer1 = get_tracer("service-1")
    tracer2 = get_tracer("service-2")
    assert tracer1 is not tracer2


def test_invalid_environment(mock_xray_recorder):
    """Test behavior with invalid environment"""
    with patch.dict("os.environ", {"APP_ENVIRONMENT": "invalid"}):
        with patch(
            "app.helpers.tracer.cloud.xray_recorder", mock_xray_recorder
        ):
            # Should default to CloudTracer for non-local environments
            tracer = TracerFactory.create_tracer("test-service")
            assert isinstance(tracer, CloudTracer)


def test_environment_case_insensitive(mock_xray_recorder):
    """Test environment string case insensitivity"""
    with patch.dict("os.environ", {"APP_ENVIRONMENT": "LOCAL"}):
        tracer = TracerFactory.create_tracer("test-service")
        assert isinstance(tracer, LocalTracer)

    with patch.dict("os.environ", {"APP_ENVIRONMENT": "CLOUD"}):
        with patch(
            "app.helpers.tracer.cloud.xray_recorder", mock_xray_recorder
        ):
            tracer = TracerFactory.create_tracer("test-service")
            assert isinstance(tracer, CloudTracer)
