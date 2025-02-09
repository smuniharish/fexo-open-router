from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from functions.pydantic_models import SearchDto, SearchItemNameSuggestDto, SearchItemNameSpellCheckerDto, \
    SearchItemProviderNameSuggestDto
from functions.search_with_filters import search_item_name_suggester, search_item_name_spell_checker, \
    search_item_name_ss, search_item_name_with_vectors, search_item_name_string_with_vectors, \
    search_item_name_with_vectors_general, search_provider_item_name_suggester
from helpers.constants.sorting_types import SortingTypesEnum
from database.solrdb import get_client, close_client
import orjson


@asynccontextmanager
async def lifespan(application:FastAPI):
    get_client()
    yield
    await close_client()

app = FastAPI(
    title="Search System",
    summary="Search System",
    description="Search System",
    version="0.0.1",
    lifespan=lifespan,
    root_path="/search-system"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can specify the allowed origins here
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods like GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],  # Allows all headers
)

class ORJSONResponse(JSONResponse):
    def render(self, content: any) -> bytes:
        return orjson.dumps(content)

FastAPI.default_response_class = ORJSONResponse

@app.get("/get_sorting_params")
async def get_sorting_params():
    return {"data": [{"key": sorting_type.name, "value": sorting_type.value} for sorting_type in SortingTypesEnum]}


@app.post("/item_name_suggest")
async def item_name_suggest(body: SearchItemNameSuggestDto):
    try:
        response = await search_item_name_suggester(body.text)
        return {"data": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.post("/provider_item_name_suggest")
async def provider_item_name_suggest(body: SearchItemProviderNameSuggestDto):
    try:
        response = await search_provider_item_name_suggester(body.text,body.latitude,body.longitude,body.radius_km)
        return {"data": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search_item_name_with_vt")
async def search_item_name_with_vt(body: SearchDto):
    filters = {
        "provider_status_filter": None,
        "item_status_filter": None,
        "domains_filter": None,
        "provider_names_filter": None,
        "item_selling_price_filter": None,
        "item_discount_percentage_filter": None
    }
    if body.filters is not None:
        filters["provider_status_filter"] = getattr(body.filters.provider_status_filter, "value", None)
        filters["item_status_filter"] = getattr(body.filters.item_status_filter, "value", None)
        filters["domains_filter"] = getattr(body.filters, "domains_filter", None)
        filters["provider_names_filter"] = getattr(body.filters, "provider_names_filter", None)
        filters["item_selling_price_filter"] = getattr(body.filters, "item_selling_price_filter", None)
        filters["item_discount_percentage_filter"] = getattr(body.filters, "item_discount_percentage_filter", None)

    try:
        response = await search_item_name_with_vectors(body.search_text, body.latitude, body.longitude, body.radius_km, body.pageNo, body.pageSize, body.sorted_by.value, filters)
        return {"data": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.post("/search_item_name_with_vt_general")
async def search_item_name_with_vt_general(body: SearchDto):
    filters = {
        "provider_status_filter": None,
        "item_status_filter": None,
        "domains_filter": None,
        "provider_names_filter": None,
        "item_selling_price_filter": None,
        "item_discount_percentage_filter": None
    }
    if body.filters is not None:
        filters["provider_status_filter"] = getattr(body.filters.provider_status_filter, "value", None)
        filters["item_status_filter"] = getattr(body.filters.item_status_filter, "value", None)
        filters["domains_filter"] = getattr(body.filters, "domains_filter", None)
        filters["provider_names_filter"] = getattr(body.filters, "provider_names_filter", None)
        filters["item_selling_price_filter"] = getattr(body.filters, "item_selling_price_filter", None)
        filters["item_discount_percentage_filter"] = getattr(body.filters, "item_discount_percentage_filter", None)

    try:
        response = await search_item_name_with_vectors_general(body.search_text, body.latitude, body.longitude, body.radius_km, body.pageNo, body.pageSize, body.sorted_by.value, filters)
        return {"data": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.post("/search_item_name_string_with_vt")
async def search_item_name_string_with_vt(body: SearchDto):
    filters = {
        "provider_status_filter": None,
        "item_status_filter": None,
        "domains_filter": None,
        "provider_names_filter": None,
        "item_selling_price_filter": None,
        "item_discount_percentage_filter": None
    }
    if body.filters is not None:
        filters["provider_status_filter"] = getattr(body.filters.provider_status_filter, "value", None)
        filters["item_status_filter"] = getattr(body.filters.item_status_filter, "value", None)
        filters["domains_filter"] = getattr(body.filters, "domains_filter", None)
        filters["provider_names_filter"] = getattr(body.filters, "provider_names_filter", None)
        filters["item_selling_price_filter"] = getattr(body.filters, "item_selling_price_filter", None)
        filters["item_discount_percentage_filter"] = getattr(body.filters, "item_discount_percentage_filter", None)

    try:
        response = await search_item_name_string_with_vectors(body.search_text, body.latitude, body.longitude, body.radius_km, body.pageNo, body.pageSize, body.sorted_by.value, filters)
        return {"data": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/item_name_spell_checker")
async def item_name_spell_checker(body: SearchItemNameSpellCheckerDto):
    try:
        response = await search_item_name_spell_checker(body.text)
        return {"data": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/item_name_ss")
async def item_name_ss(body: SearchItemNameSpellCheckerDto):
    try:
        response = await search_item_name_ss(body.text)
        return {"data": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))