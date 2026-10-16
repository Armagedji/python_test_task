import asyncio
import ast
import pandas as pd

from elasticsearch.helpers import async_bulk

from app.db.session import AsyncSessionLocal, engine
from app.db.base import Base
from app.models.document import Document
from app.elastic.search import get_es_client
from app.core.config import settings


async def load_data():
    """
    Функция, которая загружает данные из ``posts.csv`` в PostgreSQL и Elasticsearch.
    """
    print("Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    print("Reading CSV...")
    df = pd.read_csv("posts.csv")
    df = df.dropna(subset=["text", "created_date", "rubrics"])
    df["created_date"] = pd.to_datetime(df["created_date"], errors="coerce")
    df = df.dropna(subset=["created_date"])
    df["rubrics"] = df["rubrics"].apply(ast.literal_eval)

    print("Preparing Elasticsearch index...")
    es_client = await get_es_client()
    if await es_client.indices.exists(index=settings.ELASTICSEARCH_INDEX):
        await es_client.indices.delete(index=settings.ELASTICSEARCH_INDEX)
    await es_client.indices.create(index=settings.ELASTICSEARCH_INDEX)

    print(f"Ingesting {len(df)} documents...")
    async with AsyncSessionLocal() as session:
        db_objects = [
            Document(
                text=row["text"],
                rubrics=row["rubrics"],
                created_date=row["created_date"],
            )
            for _, row in df.iterrows()
        ]
        session.add_all(db_objects)
        await session.commit()

        for doc in db_objects:
            await session.refresh(doc)

        actions = [
            {
                "_index": settings.ELASTICSEARCH_INDEX,
                "_id": doc.id,
                "_source": {"text": doc.text},
            }
            for doc in db_objects
        ]
        if actions:
            await async_bulk(es_client, actions)

    await es_client.close()
    print("Done.")


if __name__ == "__main__":
    asyncio.run(load_data())