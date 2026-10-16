import pytest
import httpx

from app.main import app
from app.elastic import search as es_search
from app.db import session as db_session


@pytest.fixture(autouse=True)
async def reset_clients():
    es_search.es_client = None

    await db_session.engine.dispose()

    yield

    await es_search.close_es_client()
    await db_session.engine.dispose()


@pytest.fixture
async def client():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as ac:
        yield ac