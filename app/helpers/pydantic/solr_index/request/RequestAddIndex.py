from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl, field_validator

from app.helpers.Enums import ItemCurrencyEnum, ItemStatusEnum, ItemVegOrNonVegEnum
from app.helpers.Enums.collection_types_enum import CollectionTypesEnum


class RequestAddIndexDto(BaseModel):
    collection_type: CollectionTypesEnum = Field(..., description="collection type")
    id: str = Field(..., description="id of the item")
    code: str = Field(..., description="code of the item")
    domain: str = Field(..., description="domain of the item")
    bpp_id: str = Field(..., description="bpp id of the item")
    bpp_name: str = Field(..., description="bpp name of the item")
    bpp_uri: str = Field(..., description="bpp uri of the item")
    city: str = Field(..., description="city of the item")
    item_id: str = Field(..., description="item id of the item")
    item_offers: Optional[List[str]] = Field([], description="item offers of the item")
    parent_item_id: Optional[str] = Field(None, description="parent item id of the item")
    item_category_id: str = Field(..., description="item category id of the item")
    item_currency: ItemCurrencyEnum = Field(..., description="item currency of the item")
    item_measure_quantity: str = Field(..., description="item measure quantity of the item")
    item_measure_value: float = Field(..., description="item measure value of the item", ge=0)
    item_name: str = Field(..., description="item name of the item", min_length=1, max_length=100000)
    item_short_description: Optional[str] = Field("", description="item short description of the item", min_length=0, max_length=100000)
    item_long_description: Optional[str] = Field("", description="item long description of the item", min_length=0, max_length=100000)
    item_selling_price: float = Field(..., description="item selling price of the item", gt=0)
    item_mrp_price: float = Field(..., description="item mrp price of the item", ge=0)
    item_status: ItemStatusEnum = Field(..., description="item status of the item")
    item_timestamp: str = Field(..., description="item timestamp of the item")
    provider_timestamp: str = Field(..., description="provider timestamp of the item")
    item_symbol: str = Field(..., description="item symbol of the item")
    provider_symbol: str = Field(..., description="item symbol of the item")
    item_veg: Optional[ItemVegOrNonVegEnum] = Field(None, description="item veg or non-veg of the item")
    item_nonveg: Optional[ItemVegOrNonVegEnum] = Field(None, description="item veg or non-veg of the item")
    item_discount_percentage: float = Field(0, description="item discount percentage of the item", ge=0, le=100)
    item_available_count: int = Field(0, description="item available count of the item", ge=0)
    item_maximum_count: int = Field(0, description="item maximum count of the item", ge=0)
    item_cancellable_status: Optional[ItemStatusEnum] = Field(None, description="item cancellable status of the item")
    item_returnable_status: Optional[ItemStatusEnum] = Field(None, description="item returnable status of the item")
    provider_name: str = Field(..., description="provider name of the item", min_length=1, max_length=100)
    provider_status: Optional[ItemStatusEnum] = Field(None, description="provider status of the item")
    provider_geo_latitude: Decimal = Field(..., description="provider geo latitude with 6 decimal precision", max_digits=12, decimal_places=6)
    provider_geo_longitude: Decimal = Field(..., description="provider geo longitude with 6 decimal precision", max_digits=12, decimal_places=6)
    provider_id: str = Field(..., description="provider id of the item", min_length=1, max_length=50)
    provider_location_id: str = Field(..., description="provider location id of the item", min_length=1, max_length=50)
    provider_location_city: str = Field(..., description="provider location city of the item", min_length=1, max_length=50)
    provider_location_area_code: str = Field(..., description="provider location area code of the item", min_length=6, max_length=6)
    provider_location_street: Optional[str] = Field(None, description="provider location street of the item", min_length=1, max_length=1000)
    provider_min_order_value: float = Field(..., description="provider min order value")
    provider_start_time_day: int = Field(..., description="provider start time day", ge=0, le=2359)
    provider_end_time_day: int = Field(..., description="provider min order value", ge=0, le=2359)
    provider_days: List[int] = Field(..., description="provider days (1-Monday to 7-sunday)")
    provider_service_location_distance: float = Field(0, description="provider service location in km")
    provider_service_type: int = Field(..., description="provider service type (10 - 13)", ge=10, le=13)

    @field_validator("id", mode="before")
    @classmethod
    def validate_uuid(cls, value: str) -> str:
        """Ensure the value is a valid UUID and store it as a string."""
        if isinstance(value, UUID):
            return str(value)
        try:
            return str(UUID(value))
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid UUID: {value}") from e

    @field_validator("bpp_uri", "item_symbol", "provider_symbol", mode="before")
    @classmethod
    def validate_url(cls, value: str) -> str:
        """Ensure the value is a valid URL and store it as a string."""
        if isinstance(value, HttpUrl):  # Convert HttpUrl object to string
            return str(value)
        try:
            return str(HttpUrl(value))  # Validate URL format
        except ValueError as e:
            raise ValueError(f"Invalid URL: {value}") from e

    @field_validator("item_timestamp", "provider_timestamp", mode="before")
    @classmethod
    def validate_timestamp(cls, value: str) -> str:
        """Ensure the value is a valid datetime and store it as an ISO 8601 string."""
        if isinstance(value, datetime):
            return value.isoformat()  # Convert datetime object to string
        try:
            return datetime.fromisoformat(value).isoformat()  # Validate and standardize
        except ValueError as e:
            raise ValueError(f"Invalid datetime: {value}") from e

    @field_validator("provider_days", mode="before")
    @classmethod
    def validate_days_list(cls, values: List[int]) -> List[int]:
        """Ensure the days are valid and given with in the range."""
        try:
            if not all(1 <= day <= 7 for day in values):
                raise ValueError(f"All days must be between 1 and 7. Received: {values}")
            return values
        except ValueError as e:
            raise ValueError(f"Invalid provider days: {values}") from e
