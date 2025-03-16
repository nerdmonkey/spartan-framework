import os
from unittest.mock import patch

import pytest

from app.helpers.tracer.factory import (
    CloudTracer,
    LocalTracer,
    TracerFactory,
    get_tracer,
    validate_service_name,
)


class TestTracerFactory:
    def test_create_tracer_local_environment(self):
        """Test tracer creation in local environment"""
        with patch.dict(os.environ, {"APP_ENVIRONMENT": "local"}):
            tracer = TracerFactory.create_tracer("test-service")
            assert isinstance(tracer, LocalTracer)
            assert tracer.service_name == "test-service"

    def test_create_tracer_production_environment(self):
        """Test tracer creation in production environment"""
        with patch.dict(os.environ, {"APP_ENVIRONMENT": "production"}):
            tracer = TracerFactory.create_tracer("test-service")
            assert isinstance(tracer, CloudTracer)
            assert tracer.service_name == "test-service"

    def test_create_tracer_default_service_name(self):
        """Test tracer creation with default service name from environment"""
        with patch.dict(
            os.environ, {"APP_ENVIRONMENT": "local", "APP_NAME": "env-service"}
        ):
            tracer = TracerFactory.create_tracer()
            assert isinstance(tracer, LocalTracer)
            assert tracer.service_name == "env-service"

    def test_create_tracer_no_service_name(self):
        """Test tracer creation with no service name and no environment default"""
        with patch.dict(os.environ, {"APP_ENVIRONMENT": "local"}):
            tracer = TracerFactory.create_tracer()
            assert isinstance(tracer, LocalTracer)
            assert tracer.service_name == "spartan"


class TestValidateServiceName:
    def test_valid_service_name(self):
        """Test validation with valid service name"""
        result = validate_service_name("test-service")
        assert result == "test-service"

    def test_service_name_with_spaces(self):
        """Test validation with service name containing spaces"""
        result = validate_service_name("  test-service  ")
        assert result == "test-service"

    @pytest.mark.parametrize(
        "invalid_name",
        [
            "",
            None,
            "   ",
        ],
    )
    def test_invalid_service_name(self, invalid_name):
        """Test validation with invalid service names"""
        with pytest.raises(ValueError, match="Invalid service name"):
            validate_service_name(invalid_name)


class TestGetTracer:
    def test_get_tracer_caching(self):
        """Test that get_tracer caches results"""
        with patch.dict(os.environ, {"APP_ENVIRONMENT": "local"}):
            tracer1 = get_tracer("test-service")
            tracer2 = get_tracer("test-service")
            assert tracer1 is tracer2  # Check if same instance is returned

    def test_get_tracer_different_services(self):
        """Test that get_tracer returns different instances for different services"""
        with patch.dict(os.environ, {"APP_ENVIRONMENT": "local"}):
            tracer1 = get_tracer("service1")
            tracer2 = get_tracer("service2")
            assert tracer1 is not tracer2

    def test_get_tracer_clear_cache(self):
        """Test clearing the lru_cache"""
        with patch.dict(os.environ, {"APP_ENVIRONMENT": "local"}):
            tracer1 = get_tracer("test-service")
            get_tracer.cache_clear()
            tracer2 = get_tracer("test-service")
            assert tracer1 is not tracer2

    @pytest.fixture(autouse=True)
    def clear_cache(self):
        """Fixture to clear the cache before and after each test"""
        get_tracer.cache_clear()
        yield
        get_tracer.cache_clear()
