import os
from typing import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

from social_media_fapi.routers.post import comment_table, post_table

# This is used to overwrite the main envrionment settings by setting the envrionment to use test database.
os.environ["ENV_STATE"] = "test"

# the # noqa: E402  tells the ruff linter to ignore the rule to put this import to the top of hte file.
from social_media_fapi.main import app # noqa: E402 


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
    post_table.clear()
    comment_table.clear()
    yield


@pytest.fixture()
async def async_client() -> AsyncGenerator:
    from social_media_fapi.main import app  # Import your FastAPI app here

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
