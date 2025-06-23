import asyncio
import logging
from typing import Any, Dict, List, cast

import httpx
from fastapi import HTTPException

from app.database.mongodb import update_indexed_field
from app.database.solr.db import get_solr_client
from app.helpers.Enums import CollectionTypesEnum
from app.helpers.TypedDicts.process_document_types import ProcessDocumentType
from app.helpers.utilities.envVar import envConfig

logger = logging.getLogger(__name__)

SOLR_CORE_URLS = {
    CollectionTypesEnum.GROCERY: envConfig.solr_base_url + envConfig.solr_grocery_core + "/update/json/docs",
    CollectionTypesEnum.FNB: envConfig.solr_base_url + envConfig.solr_fnb_core + "/update/json/docs",
    CollectionTypesEnum.ELECTRONICS: envConfig.solr_base_url + envConfig.solr_electronics_core + "/update/json/docs",
}


async def send_to_solr(collection_type: CollectionTypesEnum, url: str, docs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Send documents to a specific Solr core asynchronously."""
    try:
        # client = circuit_http_client
        # response = await client.request(
        #     "POST",
        #     url,
        #     json=docs,
        #     headers={"Content-Type": "application/json"},
        # )
        # response.raise_for_status()
        # return {str(collection_type.value): {"success": True, "count": len(docs), "docs": docs}}
        client = get_solr_client()
        if not client:
            raise Exception("Solr client is not initialized.")
        response = await client.post(
            url,
            json=docs,
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()
        return {str(collection_type.value): {"success": True, "count": len(docs), "docs": docs}}
    except httpx.HTTPStatusError as e:
        return {str(collection_type): {"success": False, "error": f"Solr indexing error: {str(e)}"}}
    except httpx.RequestError as e:
        return {str(collection_type): {"success": False, "error": f"Request error: {str(e)}"}}


async def index_documents(docs: List[ProcessDocumentType]) -> Dict[str, Any]:
    """Distribute documents to respective Solr cores and send them in parallel."""
    grouped_docs: Dict[CollectionTypesEnum, List[Dict[str, Any]]] = {
        CollectionTypesEnum.GROCERY: [],
        CollectionTypesEnum.FNB: [],
        CollectionTypesEnum.ELECTRONICS: [],
    }

    for item in docs:
        collection_type = item["collection_type"]
        document = item["doc"]

        # Explicit cast to Dict[str, Any] for MyPy
        grouped_docs[collection_type].append(cast(Dict[str, Any], document))

    tasks = [send_to_solr(collection_type, SOLR_CORE_URLS[collection_type], documents) for collection_type, documents in grouped_docs.items() if documents]

    results = await asyncio.gather(*tasks)

    final_result = {}
    for result in results:
        final_result.update(result)

    return final_result


async def post_search_in_solr(solr_url: str, params: dict) -> Any:
    try:
        # client = circuit_http_client
        # response = await client.request("POST", solr_url, data=params)
        # response.raise_for_status()
        # return response.json()
        client = get_solr_client()
        if not client:
            raise Exception("Solr client is not initialized.")
        query_params = []
        from urllib.parse import urlencode

        for key, value in params.items():
            if isinstance(value, list):
                for item in value:
                    query_params.append((key, item))
            else:
                query_params.append((key, value))

        # Encode params to application/x-www-form-urlencoded
        encoded_params = urlencode(query_params)
        print("encoded_params", encoded_params)
        response = await client.post(solr_url, content=encoded_params, headers={"Content-Type": "application/x-www-form-urlencoded"})
        # response = await client.post(solr_url, data=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in solr search:{str(e)}") from e


async def batch_index_to_solr(processed_documents: List[ProcessDocumentType]) -> Any:
    """Batch index documents to Solr in chunks."""
    batch_size = 500
    results = []

    for i in range(0, len(processed_documents), batch_size):
        batch = processed_documents[i : i + batch_size]
        result = await index_documents(batch)

        # Group indexed IDs by collection_type
        # collection_wise_ids: Dict[CollectionTypesEnum, List[str]] = {}
        final_doc_ids: List[str] = []

        for _, collection_data in result.items():
            if collection_data.get("success"):
                docs = collection_data.get("docs", [])
                doc_ids = [doc["id"] for doc in docs if "id" in doc]
                # if doc_ids:
                #     collection_wise_ids[CollectionTypesEnum(collection_key)] = doc_ids
                final_doc_ids = final_doc_ids + doc_ids

        # Update MongoDB per collection type
        # update_tasks = [update_indexed_field(collection_type, ids) for collection_type, ids in collection_wise_ids.items()]
        await update_indexed_field(final_doc_ids)

        results.append(result)

    return results
