from elasticsearch import AsyncElasticsearch, NotFoundError
from app.core.config import settings
from typing import List, Optional

es_client: Optional[AsyncElasticsearch] = None


async def get_es_client() -> AsyncElasticsearch:
    """
    Возвращает глобальный асинхронный клиент Elasticsearch.
    """
    global es_client
    if es_client is None:
        es_client = AsyncElasticsearch([settings.ELASTICSEARCH_URL])
    return es_client


async def close_es_client():
    """
    Закрывает глобальный клиент Elasticsearch.
    """
    global es_client
    if es_client:
        await es_client.close()
        es_client = None


async def search_documents_by_text(text: str, size: int = 20) -> List[int]:
    """
    Выполняет полнотекстовый поиск по полю ``text`` в индексе Elasticsearch.
    """
    client = await get_es_client()
    try:
        response = await client.search(
            index=settings.ELASTICSEARCH_INDEX,
            query={"match": {"text": text}},
            size=size,
        )
        return [int(hit["_id"]) for hit in response["hits"]["hits"]]
    except NotFoundError:
        return []


async def delete_document_from_index(document_id: int) -> None:
    """
        Удаляет документ из индекса Elasticsearch по его идентификатору.
    """
    client = await get_es_client()
    try:
        await client.delete(index=settings.ELASTICSEARCH_INDEX, id=str(document_id))
    except NotFoundError:
        pass
