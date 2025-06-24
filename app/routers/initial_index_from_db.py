import asyncio
from typing import Any, List

from fastapi import APIRouter, BackgroundTasks

from app.database.mongodb import get_source_documents
from app.helpers.Enums.mongo_status_enum import MongoStatusEnum
from app.helpers.pydantic.initial_index_from_db.request.RequestInitialIndexDB import RequestInitialIndexDb
from app.helpers.TypedDicts.process_document_types import MongoValidDocsType
from app.helpers.workers.mongo_worker import add_to_mongo_queue

router = APIRouter(prefix="/initial-index-db", tags=["initial-index-db"])


async def index_documents(body: RequestInitialIndexDb) -> None:
    batch = body.batch
    skip = body.skip
    mul = body.mul
    collection_type = body.collection_type
    while True:
        valid_docs = await get_source_documents(collection_type, batch, skip, MongoStatusEnum.NEW)
        if len(valid_docs) == 0:
            break
        if mul:
            args: List[MongoValidDocsType] = [{"collection_type": collection_type, "doc": doc} for doc in valid_docs]
            # processed_docs = create_process_in_pool(add_to_mongo_queue, args)
            # await bulk_add_to_mongo_queue(args)
            await asyncio.gather(*(add_to_mongo_queue(doc) for doc in args))
        else:
            final_docs: List[MongoValidDocsType] = [{"collection_type": collection_type, "doc": doc} for doc in valid_docs]
            await asyncio.gather(*(add_to_mongo_queue(doc) for doc in final_docs))
        skip += batch


@router.post("/")
def initial_process(body: RequestInitialIndexDb, background_tasks: BackgroundTasks) -> dict[Any, Any]:
    background_tasks.add_task(index_documents, body)
    return {"message": "initialized at background"}
