from typing import Any

from fastapi import APIRouter, HTTPException

from app.helpers.Enums import SortingTypesEnum
from app.helpers.pydantic.discovery.request import SearchDto, SearchItemProviderNameSuggestDto, SearchProvidersDto, SearchSubCategoriesDto
from app.services.solr.discovery import search_item_name_string_with_vectors, search_item_name_with_vectors, search_provider_item_name_suggest, search_providers, search_sub_categories

router = APIRouter(prefix="/discovery", tags=["discovery"])


@router.post("/provider_item_name_suggest")
async def provider_item_name_suggest(body: SearchItemProviderNameSuggestDto) -> dict[Any, Any]:
    try:
        response = await search_provider_item_name_suggest(body.search_type, body.text, body.latitude, body.longitude, body.radius_km)
        return {"data": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/search_item_name_with_vt")
async def search_item_name_with_vt(body: SearchDto) -> Any:
    filters = {"provider_status_filter": None, "item_status_filter": None, "domains_filter": None, "item_category_id_filter": None, "provider_names_filter": None, "item_selling_price_filter": None, "item_discount_percentage_filter": None, "verified_filter": None}
    if body.filters is not None:
        filters["provider_status_filter"] = getattr(body.filters.provider_status_filter, "value", None)
        filters["item_status_filter"] = getattr(body.filters.item_status_filter, "value", None)
        filters["domains_filter"] = getattr(body.filters, "domains_filter", None)
        filters["item_category_id_filter"] = getattr(body.filters, "item_category_id_filter", None)
        filters["provider_names_filter"] = getattr(body.filters, "provider_names_filter", None)
        filters["item_selling_price_filter"] = getattr(body.filters, "item_selling_price_filter", None)
        filters["item_discount_percentage_filter"] = getattr(body.filters, "item_discount_percentage_filter", None)
        filters["verified_filter"] = getattr(body.filters, "verified_filter", None)
    final_sortby_value = body.sorted_by.value if body.sorted_by else SortingTypesEnum.RELEVANCE.value
    try:
        response = await search_item_name_with_vectors(body.search_type, body.search_text, body.latitude, body.longitude, body.radius_km, body.pageNo, body.pageSize, final_sortby_value, filters)
        return {"data": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/search_item_name_string_with_vt")
async def search_item_name_string_with_vt(body: SearchDto) -> Any:
    filters = {"provider_status_filter": None, "item_status_filter": None, "domains_filter": None, "item_category_id_filter": None, "provider_names_filter": None, "item_selling_price_filter": None, "item_discount_percentage_filter": None, "verified_filter": None}
    if body.filters is not None:
        filters["provider_status_filter"] = getattr(body.filters.provider_status_filter, "value", None)
        filters["item_status_filter"] = getattr(body.filters.item_status_filter, "value", None)
        filters["domains_filter"] = getattr(body.filters, "domains_filter", None)
        filters["item_category_id_filter"] = getattr(body.filters, "item_category_id_filter", None)
        filters["provider_names_filter"] = getattr(body.filters, "provider_names_filter", None)
        filters["item_selling_price_filter"] = getattr(body.filters, "item_selling_price_filter", None)
        filters["item_discount_percentage_filter"] = getattr(body.filters, "item_discount_percentage_filter", None)
        filters["verified_filter"] = getattr(body.filters, "verified_filter", None)
    final_sortby_value = body.sorted_by.value if body.sorted_by else SortingTypesEnum.RELEVANCE.value
    try:
        response = await search_item_name_string_with_vectors(body.search_type, body.search_text, body.latitude, body.longitude, body.radius_km, body.pageNo, body.pageSize, final_sortby_value, filters)
        return {"data": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/search_providers")
async def search_providers_route(body: SearchProvidersDto) -> Any:
    filters = {"provider_status_filter": None, "item_category_id_filter": None, "provider_names_filter": None, "verified_filter": None}
    if body.filters is not None:
        filters["provider_status_filter"] = getattr(body.filters.provider_status_filter, "value", None)
        # filters["item_status_filter"] = getattr(body.filters.item_status_filter, "value", None)
        # filters["domains_filter"] = getattr(body.filters, "domains_filter", None)
        filters["item_category_id_filter"] = getattr(body.filters, "item_category_id_filter", None)
        filters["provider_names_filter"] = getattr(body.filters, "provider_names_filter", None)
        # filters["item_selling_price_filter"] = getattr(body.filters, "item_selling_price_filter", None)
        # filters["item_discount_percentage_filter"] = getattr(body.filters, "item_discount_percentage_filter", None)
        filters["verified_filter"] = getattr(body.filters, "verified_filter", None)
    try:
        response = await search_providers(body.search_type, body.search_text, body.latitude, body.longitude, body.radius_km, body.pageNo, body.pageSize, filters)
        return {"data": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/search_sub_categories")
async def search_sub_categories_route(body: SearchSubCategoriesDto) -> Any:
    # filters = {"provider_status_filter": None, "item_category_id_filter": None, "provider_names_filter": None, "verified_filter": None}
    # if body.filters is not None:
    #     filters["provider_status_filter"] = getattr(body.filters.provider_status_filter, "value", None)
    #     # filters["item_status_filter"] = getattr(body.filters.item_status_filter, "value", None)
    #     # filters["domains_filter"] = getattr(body.filters, "domains_filter", None)
    #     filters["item_category_id_filter"] = getattr(body.filters, "item_category_id_filter", None)
    #     filters["provider_names_filter"] = getattr(body.filters, "provider_names_filter", None)
    #     # filters["item_selling_price_filter"] = getattr(body.filters, "item_selling_price_filter", None)
    #     # filters["item_discount_percentage_filter"] = getattr(body.filters, "item_discount_percentage_filter", None)
    #     filters["verified_filter"] = getattr(body.filters, "verified_filter", None)
    try:
        response = await search_sub_categories(body.search_type, body.latitude, body.longitude, body.radius_km)
        return {"data": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
