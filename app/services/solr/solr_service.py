import logging
from typing import Any

from app.helpers.models.text_embeddings import generate_text_embeddings
from app.helpers.pydantic.solr_index.request.RequestAddIndex import RequestAddIndexDto
from app.helpers.workers.solr_worker import add_to_queue

logger = logging.getLogger(__name__)


def process_document(document: RequestAddIndexDto) -> Any:
    item_name = document.item_name
    item_short_desc = document.item_short_description
    item_long_desc = document.item_long_description
    provider_name = document.provider_name

    item_name_vector = generate_text_embeddings(item_name).tolist()
    item_short_desc_vector = generate_text_embeddings(item_short_desc).tolist() if item_short_desc is not None else None
    item_long_desc_vector = generate_text_embeddings(item_long_desc).tolist() if item_long_desc is not None else None
    provider_name_vector = generate_text_embeddings(provider_name).tolist()

    item_name_suggester_payload = f"{document.item_symbol} | item_name"
    provider_name_suggester_payload = f"{document.provider_symbol} | provider_name"

    provider_geo = f"{document.provider_geo_latitude},{document.provider_geo_longitude}"

    doc = {
        "id": document.id,
        "code": document.code,
        "domain": document.domain,
        "bpp_id": document.bpp_id,
        "bpp_name": document.bpp_name,
        "bpp_uri": document.bpp_uri,
        "city": document.city,
        "item_id": document.item_id,
        "item_offers": document.item_offers,
        "parent_item_id": document.parent_item_id,
        "item_category_id": document.item_category_id,
        "item_currency": document.item_currency.value if document.item_currency is not None else None,
        "item_measure_quantity": document.item_measure_quantity,
        "item_measure_value": document.item_measure_value,
        "item_name": item_name,
        "item_name_vector": item_name_vector,
        "item_short_desc": item_short_desc,
        "item_short_desc_vector": item_short_desc_vector,
        "item_long_desc": item_long_desc,
        "item_long_desc_vector": item_long_desc_vector,
        "item_name_suggester_payload": item_name_suggester_payload,
        "provider_name_suggester_payload": provider_name_suggester_payload,
        "item_selling_price": document.item_selling_price,
        "item_mrp_price": document.item_mrp_price,
        "item_discount_percentage": document.item_discount_percentage,
        "item_status": document.item_status.value if document.item_status is not None else None,
        "item_timestamp": document.item_timestamp,
        "provider_timestamp": document.provider_timestamp,
        "item_symbol": document.item_symbol,
        "item_veg": document.item_veg.value if document.item_veg is not None else None,
        "item_nonveg": document.item_nonveg.value if document.item_nonveg is not None else None,
        "item_available_count": document.item_available_count,
        "item_maximum_count": document.item_maximum_count,
        "item_cancellable_status": document.item_cancellable_status.value if document.item_cancellable_status is not None else None,
        "item_returnable_status": document.item_returnable_status.value if document.item_returnable_status is not None else None,
        "provider_name": provider_name,
        "provider_name_vector": provider_name_vector,
        "provider_symbol": document.provider_symbol,
        "provider_status": document.provider_status.value if document.provider_status is not None else None,
        "provider_geo": provider_geo,
        "provider_id": document.provider_id,
        "provider_location_id": document.provider_location_id,
        "provider_location_city": document.provider_location_city,
        "provider_location_area_code": document.provider_location_area_code,
        "provider_location_street": document.provider_location_street,
    }
    return doc


async def add_to_index(document: RequestAddIndexDto) -> Any:
    doc = process_document(document)
    logger.info(doc)
    result = await add_to_queue(doc)
    return result
