from typing import Any

from fastapi import APIRouter

from app.helpers.pydantic.solr_index.request.RequestAddIndex import RequestAddIndexDto
from app.helpers.pydantic.solr_index.response.ResponseAddIndex import ResponseAddIndexDto
from app.services.solr.solr_service import add_to_index

router = APIRouter(prefix="/solr-index", tags=["solr-index"])


@router.post("/", response_model=ResponseAddIndexDto)
# @router.post("/")
async def add_index(body: RequestAddIndexDto) -> dict[Any, Any]:
    result = await add_to_index(body)
    # return result
    if result:
        return {"status": "ACK"}
    return {"status": "NACK"}
