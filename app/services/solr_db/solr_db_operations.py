import logging
from typing import Any, List

import httpx
from fastapi import HTTPException

from app.database.solr.db import get_client
from app.helpers.utilities.envVar import envConfig

logger = logging.getLogger(__name__)

SOLR_URL: str = envConfig.solr_base_url + "/update/json/docs"
# SOLR_URL: str = envConfig.solr_base_url + "/update/json/docs"


async def index_documents(documents: List[dict]) -> Any:
    client = get_client()
    try:
        response = await client.post(SOLR_URL, json=documents, headers={"Content-Type": "application/json"})
        response.raise_for_status()
        return {"indexed_documents": len(documents)}
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=500, detail=f"Solr indexing error:{str(e)}") from e
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Request error:{str(e)}") from e


async def post_search_in_solr(solr_url: str, params: dict) -> Any:
    client = get_client()
    try:
        response = await client.post(solr_url, data=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in solr search:{str(e)}") from e


async def batch_index_to_solr(processed_documents: List[dict]) -> Any:
    batch_size = 100
    for i in range(0, len(processed_documents), batch_size):
        batch = processed_documents[i : i + batch_size]
        result = await index_documents(batch)
        logger.info(result)
        return result
