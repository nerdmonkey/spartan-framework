import pytest
from starlette.testclient import TestClient
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from public.main import app
from app.models.base import Base  # Import your SQLAlchemy Base here
from app.models.user import User
from config.database import get_session  # Import the get_db dependency

get_db = get_session()

# Assuming you have a way to configure your app to use this test database
TEST_DATABASE_URL = "sqlite:///./database/spartan.db"

@pytest.fixture(scope="module")
def test_db_session():
    # Setup: Create a new test database
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create a new session for the test
    db = TestingSessionLocal()

    yield db  # Use the session in tests

    # Teardown: Drop the test database
    db.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def test_data(test_db_session):
    # Create test data (5 users)
    users = [
        User(username=f"testuser{i}", email=f"testuser{i}@example.com", password="password123")
        for i in range(1, 6)
    ]

    for user in users:
        test_db_session.add(user)
    test_db_session.commit()

    yield users  # Yield the users for use in tests

    # Teardown: Remove test data
    for user in users:
        test_db_session.delete(user)
    test_db_session.commit()

@pytest.fixture(scope="function")
def client(test_db_session):
    # Override the get_db dependency to use the test database session
    app.dependency_overrides[get_db] = lambda: test_db_session

    # Create and yield a test client for the FastAPI app
    with TestClient(app) as test_client:
        yield test_client

    # Clear the dependency overrides after the test is done
    app.dependency_overrides.clear()
