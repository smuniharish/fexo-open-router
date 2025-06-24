import asyncio
import logging
from typing import Any, List

from app.database.mongodb import get_documents_with_status, update_status_field_with_ids
from app.helpers.Enums.mongo_status_enum import MongoStatusEnum
from app.helpers.models.text_embeddings import generate_text_embeddings
from app.helpers.TypedDicts.process_document_types import ProcessDocumentType, ProcessedDocumentDocType
from app.helpers.utilities.check_url_valid_head import check_url_valid_head
from app.helpers.utilities.text import clean_text

logger = logging.getLogger(__name__)


def process_document(individual_doc: Any) -> ProcessDocumentType | None:
    collection_type = individual_doc["collection_type"]
    document = individual_doc["doc"]
    try:
        item_name = clean_text(document["item_name"])
        item_short_desc = clean_text(document["item_short_description"])
        item_long_desc = clean_text(document["item_long_description"])
        provider_name = clean_text(document["provider_name"])
        provider_id = document["provider_id"]

        item_symbol = document["item_symbol"]
        provider_symbol = document["provider_symbol"]
        latitude = document["provider_geo_latitude"]
        longitude = document["provider_geo_longitude"]

        item_name_vector = generate_text_embeddings(item_name).tolist()
        item_short_desc_vector = generate_text_embeddings(item_short_desc).tolist() if item_short_desc is not None else None
        item_long_desc_vector = generate_text_embeddings(item_long_desc).tolist() if item_long_desc is not None else None
        provider_name_vector = generate_text_embeddings(provider_name).tolist()

        item_name_suggester_payload = f"{item_symbol} | item_name"
        provider_name_suggester_payload = f"{provider_symbol} | provider_name"

        provider_geo = f"{latitude},{longitude}"

        doc: ProcessedDocumentDocType = {
            "id": document["id"],
            "code": document["code"],
            "domain": document["domain"],
            "bpp_id": document["bpp_id"],
            "bpp_name": document["bpp_name"],
            "bpp_uri": document["bpp_uri"],
            "city": document["city"],
            "item_id": document["item_id"],
            "item_offers": document["item_offers"],
            "parent_item_id": document["parent_item_id"],
            "item_category_id": document["item_category_id"],
            "item_currency": document["item_currency"] if document["item_currency"] is not None else None,
            "item_measure_quantity": document["item_measure_quantity"],
            "item_measure_value": document["item_measure_value"],
            "item_name": item_name,
            "item_name_vector": item_name_vector,
            "item_short_desc": item_short_desc,
            "item_short_desc_vector": item_short_desc_vector,
            "item_long_desc": item_long_desc,
            "item_long_desc_vector": item_long_desc_vector,
            "item_name_suggester_payload": item_name_suggester_payload,
            "item_selling_price": document["item_selling_price"],
            "item_mrp_price": document["item_mrp_price"],
            "item_discount_percentage": document["item_discount_percentage"],
            "item_status": document["item_status"] if document["item_status"] is not None else None,
            "item_timestamp": document["item_timestamp"],
            "provider_timestamp": document["provider_timestamp"],
            "item_symbol": item_symbol,
            "item_veg": document["item_veg"] if document["item_veg"] is not None else None,
            "item_nonveg": document["item_nonveg"] if document["item_nonveg"] is not None else None,
            "item_available_count": document["item_available_count"],
            "item_maximum_count": document["item_maximum_count"],
            "item_cancellable_status": document["item_cancellable_status"] if document["item_cancellable_status"] is not None else None,
            "item_returnable_status": document["item_returnable_status"] if document["item_returnable_status"] is not None else None,
            "provider_name": provider_name,
            "provider_name_suggester_payload": provider_name_suggester_payload,
            "provider_name_vector": provider_name_vector,
            "provider_symbol": provider_symbol,
            "provider_status": document["provider_status"] if document["provider_status"] is not None else None,
            "provider_geo": provider_geo,
            "provider_id": provider_id,
            "provider_location_id": document["provider_location_id"],
            "provider_location_city": document["provider_location_city"],
            "provider_location_area_code": document["provider_location_area_code"],
            "provider_location_street": document["provider_location_street"],
            "provider_min_order_value": document["provider_min_order_value"],
            "provider_start_time_day": document["provider_start_time_day"],
            "provider_end_time_day": document["provider_end_time_day"],
            "provider_days": document["provider_days"],
            "provider_service_location_distance": document["provider_service_location_distance"],
            "provider_service_type": document["provider_service_type"],
        }
        finalDoc: ProcessDocumentType = {"collection_type": collection_type, "doc": doc}
        return finalDoc
    except Exception as e:
        logger.error(f"process_document error: {e}, document: {document}")
        return None


# async def add_to_index(document: MongoValidDocsType) -> Any:
#     final_doc = process_document(document)
#     if final_doc:
#         logger.info(final_doc["doc"]["id"])
#         result = await add_to_queue(final_doc)
#         return result
#     return None


# async def add_to_mongo(document: MongoValidDocsType) -> Any:
# final_doc = process_document(document)
# if final_doc:
#     result = await add_to_mongo_queue(final_doc)
#     return result
# return None


# async def add_to_index_processed_document(docs: List[ProcessDocumentType]) -> Any:
#     if not docs:
#         return None
#     tasks = [add_to_queue(doc) for doc in docs if doc is not None]
#     results = asyncio.gather(*tasks, return_exceptions=True)
#     return results
# async def add_to_mongo_processed_document(docs: List[ProcessDocumentType]) -> Any:
#     if not docs:
#         return None
#     tasks = [add_to_mongo_queue(doc) for doc in docs if doc is not None]
#     results = asyncio.gather(*tasks, return_exceptions=True)
#     return results


async def additional_process_document(document: ProcessDocumentType) -> ProcessDocumentType | None:
    doc = document["doc"]
    item_symbol = doc.get("item_symbol")
    provider_symbol = doc.get("provider_symbol")
    if not item_symbol or not provider_symbol:
        return None
    item_valid, provider_valid = await asyncio.gather(check_url_valid_head(item_symbol), check_url_valid_head(provider_symbol))
    if not item_valid or not provider_valid:
        return None
    return document


async def process_new_stored_docs() -> List[ProcessDocumentType]:
    records = await get_documents_with_status(MongoStatusEnum.NEW)
    print("records", records)
    fetched_ids = [record["_id"] for record in records]
    await update_status_field_with_ids(fetched_ids, MongoStatusEnum.QUEUED)
    if not records:
        return []
    processed_documents = [process_document(document) for document in records]
    final_processed_documents = [doc for doc in processed_documents if doc is not None]
    if not final_processed_documents:
        return []
    tasks = [additional_process_document(doc) for doc in final_processed_documents]
    results = await asyncio.gather(*tasks)
    final_verified_documents = []
    errored_document_ids = []
    for doc, result in zip(final_processed_documents, results, strict=False):
        if result is not None:
            final_verified_documents.append(result)
        else:
            errored_document_ids.append(doc["doc"]["id"])
    if errored_document_ids:
        await update_status_field_with_ids(errored_document_ids, MongoStatusEnum.ERRORED, "Invalid Item_symbol or Provider_symbol")
    return final_verified_documents
