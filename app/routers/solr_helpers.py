from typing import Any

from fastapi import APIRouter

from app.database.mongodb import get_indexed_documents_count, get_non_indexed_documents_count

router = APIRouter(prefix="/solr-helpers", tags=["solr-helpers"])


@router.get("/solr-non-indexed-count")
async def solr_non_indexed_count() -> Any:
    return await get_non_indexed_documents_count()


@router.get("/solr-indexed-count")
async def solr_indexed_count() -> Any:
    return await get_indexed_documents_count()
