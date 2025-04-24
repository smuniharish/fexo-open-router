from typing import Any

from fastapi import APIRouter

from app.database.mongodb import get_source_documents
from app.helpers.pydantic.initial_index_from_db.request.RequestInitialIndexDB import RequestInitialIndexDb
from app.helpers.utilities.mp import create_process_in_pool
from app.services.solr.solr_service import add_to_index, add_to_index_processed_document, process_document

router = APIRouter(prefix="/initial-index-db", tags=["initial-index-db"])


@router.post("/")
async def initial_process(body: RequestInitialIndexDb) -> dict[Any, Any]:
    batch = body.batch
    skip = body.skip
    mul = body.mul
    while True:
        valid_docs = await get_source_documents(batch, skip)
        if len(valid_docs) == 0:
            break
        if mul:
            processed_docs = create_process_in_pool(process_document, valid_docs)
            await add_to_index_processed_document(processed_docs)
        else:
            for doc in valid_docs:
                await add_to_index(doc)
        skip += batch
    return {"message": "initialized"}
