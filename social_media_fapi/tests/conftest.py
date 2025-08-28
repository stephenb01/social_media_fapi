import os
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient, Request, Response

# This is used to overwrite the main envrionment settings by setting the envrionment to use test database.
os.environ["ENV_STATE"] = "test"

from social_media_fapi.database import database, user_table  # noqa: E402

# the # noqa: E402  tells the ruff linter to ignore the rule to put this import to the top of hte file.
from social_media_fapi.main import app  # noqa: E402


# This will be run once for all our test session
@pytest.fixture(scope="session")
def anyio_backend():
    """
    Using asyncio: This is just because when we use an async function in fast API,
    we need to have some sort of aync platform that it runs on.
    And we're going to tell the fast API test system to
    use the built in async IO framework for running our async tests
    """
    return "asyncio"


@pytest.fixture()
def client() -> Generator:
    yield TestClient(app)


# The autouse=True ensures this is run on every test.
@pytest.fixture(autouse=True)
async def db() -> AsyncGenerator:
    await database.connect()
    yield
    await database.disconnect()


@pytest.fixture()
async def async_client() -> AsyncGenerator:
    from social_media_fapi.main import app  # Import your FastAPI app here

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture()
async def registered_user(async_client: AsyncClient) -> dict:
    user_details = {"email": "test@example.com", "password": "1234"}
    await async_client.post("/register", json=user_details)
    query = user_table.select().where(user_table.c.email == user_details["email"])
    user = await database.fetch_one(query)
    user_details["id"] = user.id
    return user_details


@pytest.fixture()
async def confirmed_user(registered_user: dict) -> dict:
    query = (
        user_table.update()
        .where(user_table.c.email == registered_user["email"])
        .values(confirmed=True)
    )
    await database.execute(query)
    return registered_user


@pytest.fixture()
async def logged_in_token(async_client: AsyncClient, confirmed_user: dict) -> str:
    response = await async_client.post("/token", json=confirmed_user)
    assert response.status_code == 200
    return response.json().get("access_token")


@pytest.fixture(autouse=True)
def mock_httpx_client(mocker):
    mocked_client = mocker.patch("social_media_fapi.tasks.httpx.AsyncClient")

    mocked_async_client = Mock()
    response = Response(status_code=200, content="", request=Request("POST", "//"))

    mocked_async_client.post = AsyncMock(return_value=response)
    mocked_client.return_value.__aenter__.return_value = mocked_async_client

    return mocked_async_client