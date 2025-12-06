"""
Unit Test Configuration - Uses mocked dependencies for isolation with pytest-mock
"""

import os

import pytest


@pytest.fixture(scope="function", autouse=True)
def setup_test_environment():
    """Setup test environment variables."""
    os.environ["APP_ENVIRONMENT"] = "test"
