from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, CursorResult
from app.models.document import Document
from typing import List, Callable


async def get_documents_by_ids(
        db: AsyncSession, document_ids: List[int]
) -> List[Document]:
    """
    Возвращает документы по списку ID.
    """
    result = await db.execute(
        select(Document)
        .where(Document.id.in_(document_ids))
        .order_by(Document.created_date.desc())
    )
    return list(result.scalars().all())


async def delete_document_by_id(db: AsyncSession, document_id: int) -> Callable[[], int]:
    """
    Удаляет документ по его ID.
    """
    stmt = delete(Document).where(Document.id == document_id)
    result = await db.execute(stmt)
    await db.commit()

    assert isinstance(result, CursorResult)
    return result.rowcount
