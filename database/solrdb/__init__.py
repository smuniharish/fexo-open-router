import httpx
from typing import List
from fastapi import HTTPException
import os

from helpers.env_constants import get_solr_base_uri_env

SOLR_URL = get_solr_base_uri_env() + "/update/json/docs"
_client = None
# _remote_client = None

def get_client():
    global _client
    if _client is None:
        _client = httpx.AsyncClient(
            limits=httpx.Limits(
                max_connections=2000000,  # Max total connections
                max_keepalive_connections=10000,  # Max idle connections to keep alive
                keepalive_expiry=100
            )
        )
    return _client
# def get_remote_client():
#     global _remote_client
#     if _remote_client is None:
#         _remote_client = httpx.AsyncClient(
#             limits=httpx.Limits(
#                 max_connections=200000,  # Max total connections
#                 max_keepalive_connections=10000,  # Max idle connections to keep alive
#             )
#         )
#     return _remote_client

async def index_documents(solr_url: str, documents: List[dict]):
    client = get_client()
    # remote_client = get_remote_client()
    # remoteUrl = "http://10.10.10.55:8983/solr/test_v2/update/json/docs"
    try:
        response = await client.post(
            solr_url,
            json=documents,
            headers={'Content-Type': 'application/json'}
        )
        # remote_response = await remote_client.post(
        #     remoteUrl,
        #     json=documents,
        #     headers={'Content-Type': 'application/json'}
        # )
        response.raise_for_status()
        # remote_response.raise_for_status()
        return {"indexed_documents": len(documents)}
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=500, detail=f"Solr indexing error: {str(e)}")
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Request error: {str(e)}")

async def post_search_in_solr(solr_url: str, params: dict):
    client = get_client()
    try:
        response = await client.post(solr_url, data=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

async def close_client():
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None

async def batch_index_to_solr(processed_documents):
    batch_size = 100
    for i in range(0, len(processed_documents), batch_size):
        batch = processed_documents[i:i + batch_size]
        result = await index_documents(SOLR_URL, batch)
        print(result)
