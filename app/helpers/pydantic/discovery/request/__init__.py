from typing import Any, List, Optional, Tuple

from pydantic import BaseModel, Field, field_validator

from app.helpers.Enums import SearchFiltersProviderItemStatusEnum, SortingTypesEnum
from app.helpers.Enums.search_types_enum import SearchTypesEnum


class SearchItemProviderNameSuggestDto(BaseModel):
    text: str = Field(..., description="Text For Suggestions")
    search_type: SearchTypesEnum = Field(SearchTypesEnum.ALL, description="Type of search, default is ITEM_NAME")
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


class SearchFiltersDto(BaseModel):
    provider_status_filter: Optional[SearchFiltersProviderItemStatusEnum] = Field(None, description="Provider status filter")
    item_status_filter: Optional[SearchFiltersProviderItemStatusEnum] = Field(None, description="Item status filter")
    domains_filter: Optional[List[str]] = Field(None, description="List of domains")
    item_category_id_filter: Optional[SearchFiltersProviderItemStatusEnum] = Field(None, description="List of Item Category")
    provider_names_filter: Optional[List[str]] = Field(None, description="List of providers")
    item_selling_price_filter: Optional[Tuple[float, float]] = Field(None, description="Item selling price (min, max)")
    item_discount_percentage_filter: Optional[Tuple[float, float]] = Field(None, description="Item discount percentage (min, max)")

    @field_validator("item_selling_price_filter")
    def validate_item_selling_price_filter(cls, value: Optional[Tuple[float, float]]) -> Any:
        if value is not None:
            min_price, max_price = value
            if min_price > max_price:
                raise ValueError("Min price cannot be greater than max price")
        return value

    @field_validator("item_discount_percentage_filter")
    def validate_item_discount_percentage_filter(cls, value: Optional[Tuple[float, float]]) -> Any:
        if value is not None:
            min_percentage, max_percentage = value
            if min_percentage > max_percentage:
                raise ValueError("Min percentage cannot be greater than max percentage")
            if max_percentage > 100:
                raise ValueError("Max percentage cannot be greater than 100")
            if min_percentage < 0:
                raise ValueError("Min percentage cannot be less than 0")
        return value


class SearchProviderFiltersDto(BaseModel):
    provider_status_filter: Optional[SearchFiltersProviderItemStatusEnum] = Field(None, description="Provider status filter")
    item_status_filter: Optional[SearchFiltersProviderItemStatusEnum] = Field(None, description="Item status filter")
    domains_filter: Optional[List[str]] = Field(None, description="List of domains")
    item_category_id_filter: Optional[SearchFiltersProviderItemStatusEnum] = Field(None, description="List of Item Category")
    provider_names_filter: Optional[List[str]] = Field(None, description="List of providers")


class SearchDto(BaseModel):
    search_text: str = Field(..., description="Search Text", min_length=3)
    search_type: SearchTypesEnum = Field(SearchTypesEnum.ALL, description="Type of search, default is ITEM_NAME")
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


class SearchProvidersDto(BaseModel):
    search_text: str = Field("*", description="Search Text", min_length=3)
    search_type: SearchTypesEnum = Field(SearchTypesEnum.ALL, description="Type of search, default is ITEM_NAME")
    latitude: float = Field(..., description="Latitude must be between -90 and 90, up to 6 decimal places")
    longitude: float = Field(..., description="Longitude must be between -180 and 180")
    radius_km: int = Field(10, description="Search radius in kilometers")
    pageNo: int = Field(1, ge=1, description="Page number must be greater than or equal to 1")
    pageSize: int = Field(10, ge=1, le=100, description="Page size must be between 1 and 100")

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
