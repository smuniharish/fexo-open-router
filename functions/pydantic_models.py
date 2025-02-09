from pydantic import BaseModel, Field, HttpUrl, field_validator, ValidationError
from enum import Enum
from typing import List, Optional, Tuple
from datetime import datetime

from helpers.constants.sorting_types import SortingTypesEnum


class ItemDecimalEnum(str, Enum):
    enable = "enable"
    disable = "disable"


class ItemVegOrNonVeg(BaseModel):
    veg: Optional[bool] = Field(default=None)
    non_veg: Optional[bool] = Field(default=None)


class Summary(BaseModel):
    code: str
    domain: str
    bpp_id: str
    bpp_name: str
    bpp_uri: str
    city: str
    item_id: str
    item_offers: Optional[List[str]] = Field(default=None)
    parent_item_id: Optional[str] = Field(default=None)
    item_currency: str
    item_measure_quantity: str
    item_measure_value: float = Field(gt=0)
    item_name: str
    item_selling_price: float = Field(gt=0)
    item_mrp_price: float = Field(gt=0)
    item_discount_percentage: float = Field(ge=0, le=100)
    item_status: ItemDecimalEnum
    item_timestamp: datetime
    item_symbol: Optional[HttpUrl] = Field(default=None)
    item_veg_or_nonveg: ItemVegOrNonVeg
    item_short_desc: Optional[str] = Field(default=None)
    item_long_desc: Optional[str] = Field(default=None)
    item_available_count: Optional[int] = Field(default=None)
    item_maximum_count: Optional[int] = Field(default=None)
    item_cancellable_status: Optional[bool] = Field(default=None)
    item_returnable_status: Optional[bool] = Field(default=None)
    provider_name: str
    provider_status: ItemDecimalEnum
    provider_location: List[float]
    provider_id: str
    provider_location_id: str
    provider_location_city: str
    provider_location_area_code: str
    provider_location_street: Optional[str] = Field(default=None)

    class Config:
        extra = "allow"
        use_enum_values = True


class ItemDocument(BaseModel):
    summary: Summary


# API Validations
class SearchFiltersProviderItemStatusDto(Enum):
    enable = 'enable'
    disable = 'disable'


class SearchFiltersDto(BaseModel):
    provider_status_filter: Optional[SearchFiltersProviderItemStatusDto] = Field(None, description="Provider status filter")
    item_status_filter: Optional[SearchFiltersProviderItemStatusDto] = Field(None, description="Item status filter")
    domains_filter: Optional[List[str]] = Field(None, description="List of domains")
    provider_names_filter: Optional[List[str]] = Field(None, description="List of providers")
    item_selling_price_filter: Optional[Tuple[float, float]] = Field(None, description="Item selling price (min, max)")
    item_discount_percentage_filter: Optional[Tuple[float, float]] = Field(None, description="Item discount percentage (min, max)")

    @field_validator("item_selling_price_filter")
    def validate_item_selling_price_filter(cls, value: Optional[Tuple[float, float]]):
        if value is not None:
            min_price, max_price = value
            if min_price > max_price:
                raise ValueError("Min price cannot be greater than max price")
        return value

    @field_validator("item_discount_percentage_filter")
    def validate_item_discount_percentage_filter(cls, value: Optional[Tuple[float, float]]):
        if value is not None:
            min_percentage, max_percentage = value
            if min_percentage > max_percentage:
                raise ValueError("Min percentage cannot be greater than max percentage")
            if max_percentage > 100:
                raise ValueError("Max percentage cannot be greater than 100")
            if min_percentage < 0:
                raise ValueError("Min percentage cannot be less than 0")
        return value


class SearchDto(BaseModel):
    search_text: str = Field(..., description="Search Text", min_length=3)
    latitude: float = Field(..., description="Latitude must be between -90 and 90, up to 6 decimal places")
    longitude: float = Field(..., description="Longitude must be between -180 and 180")
    radius_km: int = Field(10, description="Search radius in kilometers")
    sorted_by: Optional[SortingTypesEnum] = Field(SortingTypesEnum.RELEVANCE, description="Sorting type")
    pageNo: int = Field(1, ge=1, description="Page number must be greater than or equal to 1")
    pageSize: int = Field(10, ge=1, le=100, description="Page size must be between 1 and 100")
    filters: Optional[SearchFiltersDto] = Field(None, description="Search Filters")

    @field_validator("latitude")
    def validate_latitude(cls, value: float) -> float:
        if not (-90 <= value <= 90):
            raise ValueError("Latitude must be between -90 and 90.")
        if len(str(value).split(".")[1]) > 6:
            raise ValueError("Latitude must not exceed 6 decimal places.")
        return value

    @field_validator("longitude")
    def validate_longitude(cls, value: float) -> float:
        if not (-180 <= value <= 180):
            raise ValueError("Longitude must be between -180 and 180.")
        if len(str(value).split(".")[1]) > 6:
            raise ValueError("Longitude must not exceed 6 decimal places.")
        return value


class SearchItemNameSuggestDto(BaseModel):
    text: str = Field(..., description="Text For Suggestions")

class SearchItemProviderNameSuggestDto(BaseModel):
    text: str = Field(..., description="Text For Suggestions")
    latitude: Optional[float] = Field(None, description="Latitude must be between -90 and 90, up to 6 decimal places")
    longitude: Optional[float] = Field(None, description="Longitude must be between -180 and 180")
    radius_km: Optional[int] = Field(None, description="Search radius in kilometers")

    @field_validator("latitude")
    def validate_latitude(cls, value: float) -> float:
        if not (-90 <= value <= 90):
            raise ValueError("Latitude must be between -90 and 90.")
        if len(str(value).split(".")[1]) > 6:
            raise ValueError("Latitude must not exceed 6 decimal places.")
        return value

    @field_validator("longitude")
    def validate_longitude(cls, value: float) -> float:
        if not (-180 <= value <= 180):
            raise ValueError("Longitude must be between -180 and 180.")
        if len(str(value).split(".")[1]) > 6:
            raise ValueError("Longitude must not exceed 6 decimal places.")
        return value


class SearchItemNameSpellCheckerDto(BaseModel):
    text: str = Field(..., description="Text For Spell Correction")
