from typing import Any

from fastapi import APIRouter

from app.database.mongodb.pydantic import AddIndexFromMongoDb
from app.helpers.pydantic.solr_index.request.RequestAddIndex import RequestAddIndexDto
from app.helpers.pydantic.solr_index.response.ResponseAddIndex import ResponseAddIndexDto
from app.helpers.TypedDicts.process_document_types import MongoValidDocsType
from app.helpers.workers.mongo_worker import add_to_mongo_queue

router = APIRouter(prefix="/solr-index", tags=["solr-index"])


@router.post("/", response_model=ResponseAddIndexDto)
# @router.post("/")
async def add_index(body: RequestAddIndexDto) -> dict[Any, Any]:
    data = AddIndexFromMongoDb(
        id=body.id,
        code=body.code,
        domain=body.domain,
        bpp_id=body.bpp_id,
        bpp_name=body.bpp_name,
        bpp_uri=body.bpp_uri,
        city=body.city,
        item_id=body.item_id,
        item_offers=body.item_offers,
        parent_item_id=body.parent_item_id,
        item_category_id=body.item_category_id,
        item_currency=body.item_currency,
        item_measure_quantity=body.item_measure_quantity,
        item_measure_value=body.item_measure_value,
        item_name=body.item_name,
        item_short_description=body.item_short_description,
        item_long_description=body.item_long_description,
        item_selling_price=body.item_selling_price,
        item_mrp_price=body.item_mrp_price,
        item_discount_percentage=body.item_discount_percentage,
        item_status=body.item_status,
        item_timestamp=body.item_timestamp,
        provider_timestamp=body.provider_timestamp,
        item_symbol=body.item_symbol,
        provider_symbol=body.provider_symbol,
        item_nonveg=body.item_nonveg,
        item_available_count=body.item_available_count,
        item_maximum_count=body.item_maximum_count,
        item_cancellable_status=body.item_cancellable_status,
        item_returnable_status=body.item_returnable_status,
        provider_name=body.provider_name,
        provider_status=body.provider_status,
        provider_geo_latitude=body.provider_geo_latitude,
        provider_geo_longitude=body.provider_geo_longitude,
        provider_id=body.provider_id,
        provider_location_id=body.provider_location_id,
        provider_location_city=body.provider_location_city,
        provider_location_area_code=body.provider_location_area_code,
        provider_location_street=body.provider_location_street,
        provider_min_order_value=body.provider_min_order_value,
        provider_start_time_day=body.provider_start_time_day,
        provider_end_time_day=body.provider_end_time_day,
        provider_days=body.provider_days,
        provider_service_location_distance=body.provider_service_location_distance,
        provider_service_type=body.provider_service_type,
        item_veg=body.item_veg,
    )
    final_body: MongoValidDocsType = {"collection_type": body.collection_type, "doc": data}
    result = await add_to_mongo_queue(final_body)
    # return result
    if result:
        return {"status": "ACK"}
    return {"status": "NACK"}
