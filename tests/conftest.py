import pytest
from starlette.testclient import TestClient

from public.main import app


@pytest.fixture
def client():
    """
    A pytest fixture that provides a test client for the Spartan app.

    This fixture creates a TestClient instance using the Spartan application
    imported from public.main. It's used for testing the API endpoints in the
    application. The fixture can be used in test functions to make requests to
    the API and assert the responses.

    Returns:
        TestClient: An instance of TestClient wrapped around the Spartan app.
    """
    return TestClient(app)
