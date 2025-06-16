from typing import List, Optional

from typing_extensions import TypedDict

from app.database.mongodb.pydantic import AddIndexFromMongoDb
from app.helpers.Enums import CollectionTypesEnum


class ProcessedDocumentDocType(TypedDict):
    id: str
    code: str
    domain: str
    bpp_id: str
    bpp_name: str
    bpp_uri: str
    city: str
    item_id: str
    item_offers: Optional[List[str]]
    parent_item_id: Optional[str]
    item_category_id: str
    item_currency: Optional[str]
    item_measure_quantity: Optional[str]
    item_measure_value: float
    item_name: str
    item_name_vector: List[float]
    item_short_desc: Optional[str]
    item_short_desc_vector: Optional[List[float]]
    item_long_desc: Optional[str]
    item_long_desc_vector: Optional[List[float]]
    item_name_suggester_payload: str
    item_selling_price: float
    item_mrp_price: float
    item_discount_percentage: float
    item_status: Optional[str]
    item_timestamp: str
    provider_timestamp: str
    item_symbol: str
    item_veg: Optional[str]
    item_nonveg: Optional[str]
    item_available_count: int
    item_maximum_count: int
    item_cancellable_status: Optional[str]
    item_returnable_status: Optional[str]
    provider_name: str
    provider_name_suggester_payload: str
    provider_name_vector: List[float]
    provider_symbol: str
    provider_status: Optional[str]
    provider_geo: str
    provider_id: str
    provider_location_id: str
    provider_location_city: str
    provider_location_area_code: str
    provider_location_street: Optional[str]
    provider_min_order_value: Optional[float]
    provider_start_time_day: int
    provider_end_time_day: int
    provider_days: List[int]
    provider_service_location_distance: Optional[float]
    provider_service_type: int


class ProcessDocumentType(TypedDict):
    collection_type: CollectionTypesEnum
    doc: ProcessedDocumentDocType


class MongoValidDocsType(TypedDict):
    collection_type: CollectionTypesEnum
    doc: AddIndexFromMongoDb


class ProcessedDocumentMongoDocType(TypedDict):
    _id: str
    id: str
    code: str
    domain: str
    bpp_id: str
    bpp_name: str
    bpp_uri: str
    city: str
    item_id: str
    item_offers: Optional[List[str]]
    parent_item_id: Optional[str]
    item_category_id: str
    item_currency: Optional[str]
    item_measure_quantity: Optional[str]
    item_measure_value: float
    item_name: str
    item_name_vector: List[float]
    item_short_desc: Optional[str]
    item_short_desc_vector: Optional[List[float]]
    item_long_desc: Optional[str]
    item_long_desc_vector: Optional[List[float]]
    item_name_suggester_payload: str
    item_selling_price: float
    item_mrp_price: float
    item_discount_percentage: float
    item_status: Optional[str]
    item_timestamp: str
    provider_timestamp: str
    item_symbol: str
    item_veg: Optional[str]
    item_nonveg: Optional[str]
    item_available_count: int
    item_maximum_count: int
    item_cancellable_status: Optional[str]
    item_returnable_status: Optional[str]
    provider_name: str
    provider_name_suggester_payload: str
    provider_name_vector: List[float]
    provider_symbol: str
    provider_status: Optional[str]
    provider_geo: str
    provider_id: str
    provider_location_id: str
    provider_location_city: str
    provider_location_area_code: str
    provider_location_street: Optional[str]
    provider_min_order_value: Optional[float]
    provider_start_time_day: int
    provider_end_time_day: int
    provider_days: List[int]
    provider_service_location_distance: Optional[float]
    provider_service_type: int
