import asyncio

from fastapi import APIRouter

from app.database.mongodb import get_documents_count_with_status
from app.helpers.Enums.mongo_status_enum import MongoStatusEnum

router = APIRouter(prefix="/solr-helpers", tags=["solr-helpers"])


@router.get("/solr-docs-status")
async def solr_docs_status() -> dict[str, int]:
    statuses = [
        MongoStatusEnum.NEW,
        MongoStatusEnum.QUEUED,
        MongoStatusEnum.ERRORED,
        MongoStatusEnum.INDEXED,
    ]

    raw_results = await asyncio.gather(*[get_documents_count_with_status(status) for status in statuses])

    # Extract count from result list like [{'count': 1}]
    def extract_count(result: list[dict]) -> int:
        if isinstance(result, list) and result and isinstance(result[0], dict) and "count" in result[0]:
            return int(result[0]["count"])
        return 0

    results = [extract_count(res) for res in raw_results]
    return {status.value: count for status, count in zip(statuses, results, strict=False)}
