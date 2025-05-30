import asyncio
from threading import Thread
from typing import Any, List

from fastapi import APIRouter, BackgroundTasks

from app.database.mongodb import get_source_documents
from app.helpers.pydantic.initial_index_from_db.request.RequestInitialIndexDB import RequestInitialIndexDb
from app.helpers.TypedDicts.process_document_types import MongoValidDocsType
from app.helpers.utilities.mp import create_process_in_pool
from app.services.solr.solr_service import add_to_index, add_to_index_processed_document, process_document

router = APIRouter(prefix="/initial-index-db", tags=["initial-index-db"])


async def index_documents(body: RequestInitialIndexDb) -> None:
    batch = body.batch
    skip = body.skip
    mul = body.mul
    collection_type = body.collection_type
    while True:
        valid_docs = await get_source_documents(collection_type, batch, skip)
        if len(valid_docs) == 0:
            break
        if mul:
            args: List[MongoValidDocsType] = [{"collection_type": collection_type, "doc": doc} for doc in valid_docs]
            processed_docs = create_process_in_pool(process_document, args)
            await add_to_index_processed_document(processed_docs)
        else:
            final_docs: List[MongoValidDocsType] = [{"collection_type": collection_type, "doc": doc} for doc in valid_docs]
            await asyncio.gather(*(add_to_index(doc) for doc in final_docs))
        skip += batch



@router.post("/")
def initial_process(body: RequestInitialIndexDb,background_tasks:BackgroundTasks) -> dict[Any, Any]:
    background_tasks.add_task(index_documents,body)
    return {"message": "initialized at background"}
