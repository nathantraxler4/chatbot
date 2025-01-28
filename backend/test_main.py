from unittest.mock import MagicMock, patch
from httpx import AsyncClient, ASGITransport
from jose import JWTError
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

def mock_get_user_func(token):
    if token == 'valid_token':
        return {"id": "test_user", "email": "user@example.com"}
    else:
        raise JWTError()
    
async def mock_create_func(model="", messages=""):
    mock_content = MagicMock()
    mock_content.content = "Mock LLM Response"
    
    mock_choice = MagicMock()
    mock_choice.message = mock_content

    mock_response = MagicMock()
    mock_response.choices = [mock_choice]

    return mock_response

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
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
def mock_openai_create():
    with patch("llm_service.client.chat.completions.create") as mock_create:
        mock_create.side_effect = mock_create_func
        yield mock_create

@pytest.fixture
def mock_supabase_auth():
    with patch("main.supabase.auth.get_user") as mock_get_user:
        mock_get_user.side_effect = mock_get_user_func
        yield mock_get_user

@pytest_asyncio.fixture
async def client(mock_supabase_auth, mock_openai_create):
    """
    Overrides get_session, and returns a AsyncClient.
    """
    app.dependency_overrides[get_session] = override_get_session

    # Use AsyncClient to run tests against the FastAPI app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client_db_commit_error(mock_supabase_auth):
    """Mocks a database commit error"""
    app.dependency_overrides[get_session] = mock_commit_error
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as test_client:
        yield test_client
    app.dependency_overrides.clear()


# Add this fixture
@pytest_asyncio.fixture
async def client_db_connect_error(mock_supabase_auth):
    """
    Creates a client that simulates a database connection error
    """
    async def mock_db_error():
        raise ConnectionError("Database connection failed")
    
    app.dependency_overrides[get_session] = mock_db_error
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

######## Create Tests ###########

@pytest.mark.asyncio
async def test_create_message_db_commit_error(client_db_commit_error: AsyncClient, prepare_database):
    response = await client_db_commit_error.post("/message", json={"message": "Test message"}, headers={'Authorization': 'Bearer valid_token'})
    assert response.status_code == 500
    data = response.json()
    assert data == {'detail': 'An unexpected error occurred. Please try again later.'}


@pytest.mark.asyncio
async def test_create_message_success(client: AsyncClient, prepare_database):
    response = await client.post("/message", json={ "message": "Test message" }, headers={'Authorization': 'Bearer valid_token'})
    assert response.status_code == 200
    data = response.json()
    assert data["exchange"][0]["message"] == "Test message"
    assert data["exchange"][1]["message"] == "Mock LLM Response"


@pytest.mark.asyncio
async def test_create_message_db_connect_error(client_db_connect_error):
    response = await client_db_connect_error.post("/message", json={ "message": "Test message" }, headers={'Authorization': 'Bearer valid_token'})
    assert response.status_code == 500
    data = response.json()
    assert "error" in data

@pytest.mark.asyncio
async def test_create_empty_message(client: AsyncClient, prepare_database):
    response = await client.post("/message", json={"message": ""}, headers={'Authorization': 'Bearer valid_token'})
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()

    # Test whitespace-only message
    response = await client.post("/message", json={"message": "   "}, headers={'Authorization': 'Bearer valid_token'})
    assert response.status_code == 400
    assert response.json()["detail"] == "Message cannot be empty"

@pytest.mark.asyncio
async def test_create_long_message(client: AsyncClient, prepare_database):
    long_message = "a" * 1000000  # Adjust length based on your actual limits
    response = await client.post("/message", json={"message": long_message}, headers={'Authorization': 'Bearer valid_token'})
    assert response.status_code == 200
    data = response.json()
    assert data["exchange"][0]["message"] == long_message
    assert data["exchange"][1]["message"] == "Mock LLM Response"


@pytest.mark.asyncio
async def test_create_message_invalid_json(client: AsyncClient, prepare_database):
    response = await client.post("/message", content="{invalid json}", headers={'Authorization': 'Bearer valid_token'})
    assert response.status_code == 422  # FastAPI's default validation error code

@pytest.mark.asyncio
async def test_create_message_missing_message_field(client: AsyncClient, prepare_database):
    response = await client.post("/message", json={}, headers={'Authorization': 'Bearer valid_token'})
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_create_message_wrong_message_type(client: AsyncClient, prepare_database):
    response = await client.post("/message", json={"message": 123}, headers={'Authorization': 'Bearer valid_token'})
    assert response.status_code == 422


######## Update Tests ###########

@pytest.mark.asyncio
async def test_update_message_success(client: AsyncClient, prepare_database):
    await client.post("/message", json={ "message": "Test message" }, headers={'Authorization': 'Bearer valid_token'})
    response = await client.put("/message/1", json={ "message": "Updated message" }, headers={'Authorization': 'Bearer valid_token'})
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Updated message"

@pytest.mark.asyncio
async def test_update_message_db_connect_error(client_db_connect_error: AsyncClient):
    response = await client_db_connect_error.put("/message/1", json={ "message": "Test message" }, headers={'Authorization': 'Bearer valid_token'})
    assert response.status_code == 500
    data = response.json()
    assert "error" in data

@pytest.mark.asyncio
async def test_update_message_nonexistent_message_404_error(client: AsyncClient, prepare_database):
    response = await client.put("/message/100", json={ "message": "Test message" }, headers={'Authorization': 'Bearer valid_token'})
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_update_message_empty_message(client: AsyncClient, prepare_database):
    response = await client.post("/message", json={ "message": "Test message" }, headers={'Authorization': 'Bearer valid_token'})
    user_message_id = response.json()["exchange"][0]["id"]
    response = await client.put(f"/message/{user_message_id}", json={"message": ""}, headers={'Authorization': 'Bearer valid_token'})
    assert response.status_code == 400
    assert response.json()["detail"] == "Message cannot be empty"

    # Test whitespace-only message
    response = await client.put("/message/1", json={"message": "      "}, headers={'Authorization': 'Bearer valid_token'})
    assert response.status_code == 400
    assert response.json()["detail"] == "Message cannot be empty"

@pytest.mark.asyncio
async def test_update_message_long_message(client: AsyncClient, prepare_database):
    response = await client.post("/message", json={ "message": "Test message" }, headers={'Authorization': 'Bearer valid_token'})
    user_message_id = response.json()["exchange"][0]["id"]
    long_message = "a" * 1000000  # Adjust length based on your actual limits
    response = await client.put(f"/message/{user_message_id}", json={"message": long_message}, headers={'Authorization': 'Bearer valid_token'})
    assert response.status_code == 200
    assert response.json()["message"] == long_message

@pytest.mark.asyncio
async def test_update_message_invalid_json(client: AsyncClient, prepare_database):
    response = await client.put("/message/1", content="{invalid json}", headers={'Authorization': 'Bearer valid_token'})
    assert response.status_code == 422  # FastAPI's default validation error code

@pytest.mark.asyncio
async def test_update_message_missing_message_field(client: AsyncClient, prepare_database):
    response = await client.put("/message/1", json={}, headers={'Authorization': 'Bearer valid_token'})
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_update_message_wrong_id_type_field(client: AsyncClient, prepare_database):
    response = await client.put("/message/id", json={}, headers={'Authorization': 'Bearer valid_token'})
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_update_message_wrong_message_type(client: AsyncClient, prepare_database):
    response = await client.post("/message", json={"message": 123}, headers={'Authorization': 'Bearer valid_token'})
    assert response.status_code == 422


######## Delete Tests ###########

@pytest.mark.asyncio
async def test_delete_message_success(client: AsyncClient, prepare_database):
    response = await client.post("/message", json={"message": "Test Message"}, headers={'Authorization': 'Bearer valid_token'})
    response = await client.delete("/message/1", headers={'Authorization': 'Bearer valid_token'})
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_message_noexistant_message_404_error(client: AsyncClient, prepare_database):
    response = await client.delete("/message/100", headers={'Authorization': 'Bearer valid_token'})
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_message_wrong_id_type_field(client: AsyncClient, prepare_database):
    response = await client.delete("/message/id", headers={'Authorization': 'Bearer valid_token'})
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_delete_message_db_error(client_db_connect_error: AsyncClient):
    response = await client_db_connect_error.delete("/message/1", headers={'Authorization': 'Bearer valid_token'})
    assert response.status_code == 500
    data = response.json()
    assert "error" in data

@pytest.mark.asyncio
async def test_delete_message_db_connect_error(client_db_connect_error: AsyncClient):
    response = await client_db_connect_error.delete("/message/1", headers={'Authorization': 'Bearer valid_token'})
    assert response.status_code == 500
    data = response.json()
    assert "error" in data

####### AUTH Middleware #########

@pytest.mark.asyncio
async def test_token_header_missing(client: AsyncClient):
    response = await client.delete("/message/1")
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Authorization token missing"

@pytest.mark.asyncio
async def test_token_invalid(client: AsyncClient):
    response = await client.delete("/message/1", headers={'Authorization': 'Bearer invalid_token'})
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Invalid token"