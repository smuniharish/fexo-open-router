import asyncio

from fastapi import APIRouter,Query
from fastapi.responses import StreamingResponse
from io import StringIO
import csv

from typing import Any,Optional

from app.database.mongodb import fetch_documents_by_status_and_time, get_documents_count_with_status
from app.helpers.Enums.mongo_status_enum import MongoStatusEnum

router = APIRouter(prefix="/solr-helpers", tags=["solr-helpers"])

@router.get("/solr-docs-status")
async def solr_docs_status() -> dict[str, Any]:
    statuses = [
        MongoStatusEnum.NEW,
        MongoStatusEnum.QUEUED,
        MongoStatusEnum.ERRORED,
        MongoStatusEnum.INDEXED,
    ]

    raw_results = await asyncio.gather(
        *[get_documents_count_with_status(status.value) for status in statuses]
    )

    def extract_count(result: list[dict]) -> int:
        return sum(doc.get("count", 0) for doc in result if isinstance(doc, dict))

    response = {}
    for status, docs in zip(statuses, raw_results, strict=False):
        response[status.value] = {
            "count": extract_count(docs),
            "download_link": f"/download-docs?status={status.value}"
        }

    return response

@router.get("/download-docs")
async def download_docs(
    status: str,
    start_time: Optional[str] = Query(None, description="Start time in ISO format (e.g., 2024-01-01T00:00:00)"),
    end_time: Optional[str] = Query(None, description="End time in ISO format (e.g., 2024-01-31T23:59:59)")
):
    docs = await fetch_documents_by_status_and_time(status, start_time, end_time)

    if not docs:
        return {"message": f"No documents found for status '{status}' in the given time range."}

    # Write to CSV
    csv_buffer = StringIO()
    writer = csv.DictWriter(csv_buffer, fieldnames=docs[0].keys())
    writer.writeheader()
    writer.writerows(docs)
    csv_buffer.seek(0)
    file_name=f"{status}_docs.csv"
    if(start_time):
        file_name=f"{status}_{start_time}_docs.csv"
    if(end_time):
        file_name=f"{status}_{end_time}_docs.csv"
    if start_time and end_time:
        file_name = f"{status}_{start_time}_{end_time}_docs.csv"

    return StreamingResponse(
        csv_buffer,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={file_name}"}
    )