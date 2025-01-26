from httpx import AsyncClient, ASGITransport
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from main import app
from database import get_session
from models import Base

# Create a separate async engine for tests (pointing to SQLite in memory)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine_test = create_async_engine(
    TEST_DATABASE_URL,
    echo=True,
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine_test,
    class_=AsyncSession,
    expire_on_commit=False
)

async def override_get_session():
    async with TestingSessionLocal() as session:
        yield session

async def mock_commit_error():
    async def failing_commit():
        raise Exception("Commit failed")
    
    async with TestingSessionLocal() as session:
        session.commit = failing_commit
        yield session

@pytest_asyncio.fixture
async def prepare_database():
    """
    Fixture to create and drop all tables in the test database.
    Runs once per test session.
    """
    # Create the tables
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Drop the tables after tests are done
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@pytest_asyncio.fixture
async def client():
    """
    Overrides get_session, and returns a AsyncClient.
    """
    app.dependency_overrides[get_session] = override_get_session

    # Use AsyncClient to run tests against the FastAPI app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client_db_commit_error():
    """Mocks a database commit error"""
    app.dependency_overrides[get_session] = mock_commit_error
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as test_client:
        yield test_client
    app.dependency_overrides.clear()


# Add this fixture
@pytest_asyncio.fixture
async def client_db_connect_error():
    """
    Creates a client that simulates a database connection error
    """
    async def mock_db_error():
        raise ConnectionError("Database connection failed")
    
    app.dependency_overrides[get_session] = mock_db_error
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_db_commit_error(client_db_commit_error, prepare_database):
    response = await client_db_commit_error.post("/message", json={"message": "Test message"})
    assert response.status_code == 500
    data = response.json()
    assert data == {'detail': 'An unexpected error occurred. Please try again later.'}


@pytest.mark.asyncio
async def test_create_message_success(client, prepare_database):
    response = await client.post("/message", json={ "message": "Test message" })
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Test message"


@pytest.mark.asyncio
async def test_create_message_db_error(client_db_connect_error):
    response = await client_db_connect_error.post("/message", json={ "message": "Test message" })
    assert response.status_code == 500
    data = response.json()
    assert "error" in data

@pytest.mark.asyncio
async def test_create_empty_message(client, prepare_database):
    response = await client.post("/message", json={"message": ""})
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()

    # Test whitespace-only message
    response = await client.post("/message", json={"message": "   "})
    assert response.status_code == 400
    assert response.json()["detail"] == "Message cannot be empty"

@pytest.mark.asyncio
async def test_create_long_message(client, prepare_database):
    long_message = "a" * 1000000  # Adjust length based on your actual limits
    response = await client.post("/message", json={"message": long_message})
    assert response.status_code == 200
    assert response.json()["message"] == long_message

@pytest.mark.asyncio
async def test_invalid_json(client, prepare_database):
    response = await client.post("/message", content="{invalid json}")
    assert response.status_code == 422  # FastAPI's default validation error code

@pytest.mark.asyncio
async def test_missing_message_field(client, prepare_database):
    response = await client.post("/message", json={})
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_wrong_message_type(client, prepare_database):
    response = await client.post("/message", json={"message": 123})
    assert response.status_code == 422

