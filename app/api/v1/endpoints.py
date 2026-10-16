from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import get_db
from app.schemas.document import DocumentSearchResult
from app.crud import document as crud_document
from app.elastic import search as es_search

router = APIRouter()


@router.get("/search", response_model=List[DocumentSearchResult])
async def search_documents(
        query: str = Query(..., description="The text to search for"),
        db: AsyncSession = Depends(get_db),
):
    """
    Ищет документы по текстовому запросу.
    """
    document_ids = await es_search.search_documents_by_text(query)
    if not document_ids:
        return []
    return await crud_document.get_documents_by_ids(db, document_ids)


@router.delete("/documents/{document_id}", status_code=200)
async def delete_document(
        document_id: int,
        db: AsyncSession = Depends(get_db),
):
    """
    Удаляет документ из БД и из поискового индекста.
    """
    deleted_count = await crud_document.delete_document_by_id(db, document_id)
    if deleted_count == 0:
        raise HTTPException(status_code=404, detail="Document not found in database")
    await es_search.delete_document_from_index(document_id)
    return {"message": f"Document {document_id} deleted successfully"}
