import pytest
from httpx import AsyncClient


pytestmark = pytest.mark.asyncio


async def test_search_documents(client: AsyncClient):
    """Проверяет, что поиск возвращает документы, отсортированные по дате (убывание)."""
    response = await client.get("/api/v1/search", params={"query": "конкурс"})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if data:
        dates = [doc["created_date"] for doc in data]
        assert dates == sorted(dates, reverse=True)


async def test_search_non_existent(client: AsyncClient):
    """Проверяет, что поиск несуществующего термина возвращает пустой список."""
    response = await client.get(
        "/api/v1/search", params={"query": "a_made_up_term_xyz_123"}
    )
    assert response.status_code == 200
    assert response.json() == []


async def test_delete_document(client: AsyncClient):
    """Проверяет удаление документа: 200 при первом вызове, 404 при повторном."""
    search = await client.get("/api/v1/search", params={"query": "москва"})
    docs = search.json()
    if not docs:
        pytest.skip("No documents matched the query to delete")

    doc_id = docs[0]["id"]
    delete = await client.delete(f"/api/v1/documents/{doc_id}")
    assert delete.status_code == 200

    delete_again = await client.delete(f"/api/v1/documents/{doc_id}")
    assert delete_again.status_code == 404