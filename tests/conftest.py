import pytest
from starlette.testclient import TestClient

from public.main import app


@pytest.fixture
def client():
    return TestClient(app)
