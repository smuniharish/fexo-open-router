import asyncio
import logging
from typing import Any

from app.helpers.Enums import SearchTypesEnum
from app.helpers.models.text_embeddings import generate_text_embeddings
from app.helpers.utilities.envVar import envConfig
from app.helpers.utilities.get_current_time_number import get_current_time
from app.helpers.utilities.get_day_number import get_day_number
from app.services.solr_db.solr_db_operations import post_search_in_solr

logger = logging.getLogger(__name__)

SOLR_GROCERY_SELECT_URL = envConfig.solr_base_url + envConfig.solr_grocery_core + "/select"
SOLR_FNB_SELECT_URL = envConfig.solr_base_url + envConfig.solr_fnb_core + "/select"
SOLR_ELECTRONICS_SELECT_URL = envConfig.solr_base_url + envConfig.solr_electronics_core + "/select"


SOLR_SELECT_URLS = {SearchTypesEnum.GROCERY: SOLR_GROCERY_SELECT_URL, SearchTypesEnum.ELECTRONICS: SOLR_ELECTRONICS_SELECT_URL, SearchTypesEnum.FNB: SOLR_FNB_SELECT_URL}


def parse_grouped(results: Any, parse_key: Any, type: SearchTypesEnum) -> Any:
    grouped_item_name_suggest = results.get("grouped", {}).get(parse_key, {})
    if grouped_item_name_suggest:
        grouped_data = grouped_item_name_suggest.get("groups", [])
        matches = grouped_item_name_suggest.get("matches", 0)
        # Check if there are any matching documents
        if grouped_data:
            flat_docs = [group["doclist"]["docs"][0] for group in grouped_data]

            # Merge highlighting into the docs section
            highlighting = results.get("highlighting", {})
            for doc in flat_docs:
                doc_id = doc.get("id")
                if doc_id in highlighting and parse_key in highlighting[doc_id]:
                    doc["suggest"] = highlighting[doc_id][parse_key][0]

            # Create a flat response structure
            flat_response = {
                # "responseHeader": results.get("responseHeader", {}),
                type.value: {"numFound": len(flat_docs), "matches": matches, "start": 0, "docs": flat_docs}
            }
            return flat_response
        else:
            # No matching documents
            flat_response = {
                # "responseHeader": results.get("responseHeader", {}),
                type.value: {"numFound": 0, "matches": 0, "start": 0, "docs": []}
            }
            return flat_response
    else:
        # No matching documents
        flat_response = {
            # "responseHeader": results.get("responseHeader", {}),
            type.value: {"numFound": 0, "matches": 0, "start": 0, "docs": []}
        }
        return flat_response


async def search_item_name_suggester(type: SearchTypesEnum, text_query: str, lat: float | None, lon: float | None, radius: int | None) -> Any:
    try:
        filter_query = []
        if lat and lon and radius is not None:
            filter_query.append(f"{{!geofilt sfield=provider_geo pt={lat},{lon} d = {radius}}}")
        params = {"defType": "edismax", "q": f'item_name:("{text_query}"^20) OR item_name_suggest:("{text_query}*"^10 OR "{text_query}"^5 OR "{text_query}"~1)', "fl": "id,suggest:item_name_suggest,text:item_name,payload:item_name_suggester_payload_string", "fq": filter_query, "hl": "true", "hl.fl": "item_name_suggest", "hl.simple.pre": "<b>", "hl.simple.post": "</b>", "group": "true", "group.field": "item_name_suggest", "group.limit": "1"}
        if lat and lon and radius is not None:
            params["sfield"] = "provider_geo"
            params["pt"] = f"{lat},{lon}"
        solr_url = None
        if type in SOLR_SELECT_URLS.keys():
            solr_url = SOLR_SELECT_URLS[type]
            results = await post_search_in_solr(solr_url, params)
            logger.debug(f"solr results: {results}")
            return [parse_grouped(results, "item_name_suggest", type)]
        else:
            urls = SOLR_SELECT_URLS.values()
            response = await asyncio.gather(*[post_search_in_solr(solr_url, params) for solr_url in urls])
            results = [parse_grouped(result, "item_name_suggest", type) for result, type in zip(response, SOLR_SELECT_URLS.keys(), strict=False)]
            return results
    except Exception as e:
        logger.error(f"excetion search_item_name_suggester {str(e)}")


async def search_provider_name_suggester(type: SearchTypesEnum, text_query: str, lat: float | None, lon: float | None, radius: int | None) -> Any:
    try:
        filter_query = []
        if lat and lon and radius is not None:
            filter_query.append(f"{{!geofilt sfield=provider_geo pt={lat},{lon} d = {radius}}}")
        params = {"defType": "edismax", "q": f'provider_name:("{text_query}"^20) OR provider_name_suggest:("{text_query}*"^10 OR "{text_query}"^5 OR "{text_query}"~1)', "fl": "id,suggest:provider_name_suggest,text:provider_name,payload:provider_name_suggester_payload_string", "fq": filter_query, "hl": "true", "hl.fl": "provider_name_suggest", "hl.simple.pre": "<b>", "hl.simple.post": "</b>", "group": "true", "group.field": "provider_name_suggest", "group.limit": "1"}
        if lat and lon and radius is not None:
            params["sfield"] = "provider_geo"
            params["pt"] = f"{lat},{lon}"
        solr_url = None
        if type in SOLR_SELECT_URLS.keys():
            solr_url = SOLR_SELECT_URLS[type]
            results = await post_search_in_solr(solr_url, params)
            logger.debug(f"solr results: {results}")
            return [parse_grouped(results, "provider_name_suggest", type)]
        else:
            urls = SOLR_SELECT_URLS.values()
            response = await asyncio.gather(*[post_search_in_solr(solr_url, params) for solr_url in urls])
            results = [parse_grouped(result, "provider_name_suggest", type) for result, type in zip(response, SOLR_SELECT_URLS.keys(), strict=False)]
            return results
    except Exception as e:
        logger.error(f"excetion search_provider_name_suggester:{str(e)}")


async def search_provider_item_name_suggest(type: SearchTypesEnum, text_query: str, lat: float | None, lon: float | None, radius: int | None) -> Any:
    item_suggest, provider_suggest = await asyncio.gather(search_item_name_suggester(type, text_query, lat, lon, radius), search_provider_name_suggester(type, text_query, lat, lon, radius))
    final_response = {"item_suggest": item_suggest, "provider_suggest": provider_suggest}
    return final_response


def parse_final_response_grouped(results: Any, type: SearchTypesEnum) -> Any:
    final_response = {type.value: {"grouped": results["grouped"], "filters": results["facet_counts"]}}
    return final_response


async def search_item_name_with_vectors(type: SearchTypesEnum, text_query: str, lat: float, lon: float, radius: int, page: int, rows_per_page: int, sorting_value: str, filters: Any) -> Any:
    sorting_dict = {"RELEVANCE": None, "DISTANCE_HIGH_TO_LOW": "geodist() desc", "DISTANCE_LOW_TO_HIGH": "geodist() asc", "PRICE_HIGH_TO_LOW": "item_selling_price desc", "PRICE_LOW_TO_HIGH": "item_selling_price asc"}
    logger.debug(f"sorting value :: {sorting_value}")
    logger.debug(f"filters :: {filters}")
    # filter_query=[]
    filter_query = [f"{{!geofilt sfield=provider_geo pt={lat},{lon} d = {radius}}}"]
    if filters["provider_status_filter"] is not None:
        filter_query.append(f"provider_status:{filters['provider_status_filter']}")
    if filters["item_status_filter"] is not None:
        filter_query.append(f"item_status:{filters['item_status_filter']}")
    # if filters["domains_filter"] is not None:
    #     final_domains_list = [domain.replace(":", "\\:") for domain in filters["domains_filter"]]
    #     filter_query.append(f"domain_string:{' OR '.join(final_domains_list)}")
    if filters["verified_filter"] is not None and filters["verified_filter"] == "enable":
        filter_query.append(f"bpp_id:{' OR '.join(envConfig.trusted_bpps)}")
    if filters["item_category_id_filter"] is not None:
        filter_query.append(f"item_category_id:{' OR '.join([f'"{name}"' for name in filters['item_category_id_filter']])}")
    if filters["provider_names_filter"] is not None:
        filter_query.append(f"provider_name_string:{' OR '.join([f'"{name}"' for name in filters['provider_names_filter']])}")
    if filters["item_selling_price_filter"] is not None:
        min_price, max_price = filters["item_selling_price_filter"]
        filter_query.append(f"item_selling_price:[{min_price} TO {max_price}]")
    if filters["item_discount_percentage_filter"] is not None:
        min_percentage, max_percentage = filters["item_discount_percentage_filter"]
        filter_query.append(f"item_discount_percentage:[{min_percentage} TO {max_percentage}]")

    sort_query_string = sorting_dict[sorting_value]
    start = (page - 1) * rows_per_page
    raw_vector = generate_text_embeddings(text_query)[0]
    text_query_vector = "[" + ",".join(map(str, raw_vector.tolist())) + "]"
    vector_limit = 1000
    params = {
        "defType": "edismax",
        # "q": f'item_name:"{text_query}"^10 OR item_short_desc:{text_query}^2 OR item_long_desc:{text_query}^1 ' + f"OR {{!knn f=item_name_vector topK={vector_limit}}}{text_query_vector}^3 " + f"OR {{!knn f=item_short_desc_vector topK={vector_limit}}}{text_query_vector}^2 " + f"OR {{!knn f=item_long_desc_vector topK={vector_limit}}}{text_query_vector}^1",
        "q": f'item_name:"{text_query}"^10 OR item_short_desc:{text_query}^2 OR item_long_desc:{text_query}^1 ',
        "knn.q": [f"{{!knn f=item_name_vector topK={vector_limit}}}{text_query_vector}", f"{{!knn f=item_short_desc_vector topK={vector_limit}}}{text_query_vector}", f"{{!knn f=item_long_desc_vector topK={vector_limit}}}{text_query_vector}"],
        # f"AND {{!geofilt sfield=provider_geo pt={lat},{lon} d={radius}}}",
        "fq": filter_query,
        "fl": "id,domain,bpp_id,city,item_id,item_currency,item_measure_quantity,item_measure_value,item_name,item_short_desc,item_long_desc,item_selling_price,item_mrp_price,item_discount_price,item_status,item_symbol,item_available_count,item_maximum_count,provider_name,provider_status,provider_geo,provider_id,provider_geo,provider_location_city,provider_location_area_code,provider_location_street,provider_location_id,item_veg,distance:geodist()",
        "sort": sort_query_string,
        "sfield": "provider_geo",
        "pt": f"{lat},{lon}",
        "rows": rows_per_page,
        "start": start,
        "facet": "true",
        "facet.range": ["item_selling_price", "item_discount_percentage"],
        "f.item_selling_price.facet.range.start": 0,
        "f.item_selling_price.facet.range.end": 1000000,
        "f.item_selling_price.facet.range.gap": 500,
        "f.item_selling_price.facet.mincount": 1,
        "f.item_discount_percentage.facet.range.start": 0,
        "f.item_discount_percentage.facet.range.end": 100,
        "f.item_discount_percentage.facet.range.gap": 10,
        "f.item_discount_percentage.facet.mincount": 1,
        "facet.field": ["provider_status", "item_status", "provider_name_string", "item_category_id"],
        # "facet.pivot": "item_name_string,provider_name_string",
        "group": "true",
        "group.field": "item_name_string",
        "group.sort": "item_selling_price asc",
        # "group.limit": rows_per_page,
        # "group.offset": start,
        # "group.ngroups": "true",
        "wt": "json",
    }
    if type in SOLR_SELECT_URLS.keys():
        solr_url = SOLR_SELECT_URLS[type]
        results = await post_search_in_solr(solr_url, params)
        logger.debug(f"solr results {results}")
        final_response = [parse_final_response_grouped(results, type)]
        return final_response
    else:
        urls = SOLR_SELECT_URLS.values()
        results = await asyncio.gather(*[post_search_in_solr(solr_url, params) for solr_url in urls])
        final_response = [parse_final_response_grouped(result, type) for result, type in zip(results, SOLR_SELECT_URLS.keys(), strict=False)]
        return final_response


def parse_final_response(results: Any, type: SearchTypesEnum) -> Any:
    final_response = {type.value: {"response": results["response"], "filters": results["facet_counts"]}}
    return final_response


async def search_item_name_string_with_vectors(type: SearchTypesEnum, text_query: str, lat: float, lon: float, radius: int, page: int, rows_per_page: int, sorting_value: str, filters: Any) -> Any:
    sorting_dict = {"RELEVANCE": None, "DISTANCE_HIGH_TO_LOW": "geodist() desc", "DISTANCE_LOW_TO_HIGH": "geodist() asc", "PRICE_HIGH_TO_LOW": "item_selling_price desc", "PRICE_LOW_TO_HIGH": "item_selling_price asc"}
    logger.debug(f"sorting value :: {sorting_value}")
    logger.debug(f"filters :: {filters}")
    # filter_query = []
    filter_query = [f"{{!geofilt sfield=provider_geo pt={lat},{lon} d = {radius}}}"]
    if filters["provider_status_filter"] is not None:
        filter_query.append(f"provider_status:{filters['provider_status_filter']}")
    if filters["item_status_filter"] is not None:
        filter_query.append(f"item_status:{filters['item_status_filter']}")
    if filters["verified_filter"] is not None and filters["verified_filter"] == "enable":
        filter_query.append(f"bpp_id:{' OR '.join(envConfig.trusted_bpps)}")
    if filters["item_category_id_filter"] is not None:
        filter_query.append(f"item_category_id:{' OR '.join([f'"{name}"' for name in filters['item_category_id_filter']])}")
    if filters["provider_names_filter"] is not None:
        filter_query.append(f"provider_name_string:{' OR '.join([f'"{name}"' for name in filters['provider_names_filter']])}")
    if filters["item_selling_price_filter"] is not None:
        min_price, max_price = filters["item_selling_price_filter"]
        filter_query.append(f"item_selling_price:[{min_price} TO {max_price}]")
    if filters["item_discount_percentage_filter"] is not None:
        min_percentage, max_percentage = filters["item_discount_percentage_filter"]
        filter_query.append(f"item_discount_percentage:[{min_percentage} TO {max_percentage}]")

    sort_query_string = sorting_dict[sorting_value]
    start = (page - 1) * rows_per_page
    raw_vector = generate_text_embeddings(text_query)[0]
    text_query_vector = "[" + ",".join(map(str, raw_vector.tolist())) + "]"
    vector_limit = 1000
    params = {
        "defType": "edismax",
        # "q": f'item_name:"{text_query}"^10' + f"OR {{!knn f=item_name_vector topK={vector_limit}}}{text_query_vector}^3 " + f"OR {{!knn f=item_short_desc_vector topK={vector_limit}}}{text_query_vector}^2 " + f"OR {{!knn f=item_long_desc_vector topK={vector_limit}}}{text_query_vector}^1",
        "q": f'item_name:"{text_query}"^10',
        "knn.q": [f"{{!knn f=item_name_vector topK={vector_limit}}}{text_query_vector}", f"{{!knn f=item_short_desc_vector topK={vector_limit}}}{text_query_vector}", f"{{!knn f=item_long_desc_vector topK={vector_limit}}}{text_query_vector}"],
        # f"AND {{!geofilt sfield=provider_geo pt={lat},{lon} d={radius}}}",
        "fq": filter_query,
        "fl": "id,domain,bpp_id,city,item_id,item_currency,item_measure_quantity,item_measure_value,item_name,item_short_desc,item_long_desc,item_selling_price,item_mrp_price,item_discount_price,item_status,item_symbol,item_available_count,item_maximum_count,provider_name,provider_status,provider_geo,provider_id,provider_geo,provider_location_city,provider_location_area_code,provider_location_street,provider_location_id,item_veg,distance:geodist()",
        "sort": sort_query_string,
        "sfield": "provider_geo",
        "pt": f"{lat},{lon}",
        "rows": rows_per_page,
        "start": start,
        "facet": "true",
        "facet.range": ["item_selling_price", "item_discount_percentage"],
        "f.item_selling_price.facet.range.start": 0,
        "f.item_selling_price.facet.range.end": 1000000,
        "f.item_selling_price.facet.range.gap": 500,
        "f.item_selling_price.facet.mincount": 1,
        "f.item_discount_percentage.facet.range.start": 0,
        "f.item_discount_percentage.facet.range.end": 100,
        "f.item_discount_percentage.facet.range.gap": 10,
        "f.item_discount_percentage.facet.mincount": 1,
        "facet.field": ["provider_status", "item_status", "provider_name_string", "item_category_id"],
        # "facet.pivot": "item_name_string,provider_name_string",
        # "group": "true",
        # "group.field": "item_name_string",
        # "group.sort":"item_selling_price asc",
        # "group.limit": rows_per_page,
        # "group.offset": start,
        # "group.ngroups": "true",
        "wt": "json",
    }
    if type in SOLR_SELECT_URLS.keys():
        solr_url = SOLR_SELECT_URLS[type]
        results = await post_search_in_solr(solr_url, params)
        logger.debug(f"solr results {results}")
        final_response = [parse_final_response(results, type)]
        return final_response
    else:
        urls = SOLR_SELECT_URLS.values()
        results = await asyncio.gather(*[post_search_in_solr(solr_url, params) for solr_url in urls])
        final_response = [parse_final_response(result, type) for result, type in zip(results, SOLR_SELECT_URLS.keys(), strict=False)]
        return final_response


def parse_final_providers_response(results: Any, type: SearchTypesEnum) -> Any:
    final_response = {type.value: {"grouped": results["grouped"]}}
    return final_response


def parse_sub_categories_response(results: Any, type: SearchTypesEnum) -> Any:
    facet_list = results.get("facet_counts", {}).get("facet_fields", {}).get("item_category_id", [])
    categories = [{"item_category_id": facet_list[i], "count": facet_list[i + 1]} for i in range(0, len(facet_list), 2)]
    final_response = {type.value: categories}
    return final_response


async def search_providers(type: SearchTypesEnum, text_query: str, lat: float, lon: float, radius: int, page: int, rows_per_page: int, filters: Any) -> Any:
    # filter_query=[]
    filter_query = [f"{{!geofilt sfield=provider_geo pt={lat},{lon} d={radius}}}"]
    if filters["provider_status_filter"] is not None:
        filter_query.append(f"provider_status:{filters['provider_status_filter']}")
    if filters["item_category_id_filter"] is not None:
        filter_query.append(f"item_category_id:{' OR '.join([f'"{name}"' for name in filters['item_category_id_filter']])}")
    if filters["provider_names_filter"] is not None:
        filter_query.append(f"provider_name_string:{' OR '.join([f'"{name}"' for name in filters['provider_names_filter']])}")
    if filters["verified_filter"] is not None and filters["verified_filter"] == "enable":
        filter_query.append(f"bpp_id:{' OR '.join(envConfig.trusted_bpps)}")
    today: int = get_day_number()
    current_time: int = get_current_time()

    start = (page - 1) * rows_per_page
    raw_vector = generate_text_embeddings(text_query)[0]
    text_query_vector = "[" + ",".join(map(str, raw_vector.tolist())) + "]"
    vector_limit = 1000
    params = {
        "defType": "edismax",
        # "q": f'provider_name:"{text_query}"^10' + f"OR {{!knn f=provider_name_vector topK={vector_limit}}}{text_query_vector}^3 ",
        "fq": filter_query,
        "fl": f'id,domain,item_category_id,provider_name,provider_symbol,provider_status,provider_id,provider_geo,provider_location_city,provider_location_area_code,provider_location_street,provider_location_id,provider_min_order_value,provider_start_time_day,provider_end_time_day,provider_days,provider_service_location_distance,provider_service_type,provider_symbol,availability:if(query({{!v="provider_days:{today}"}}),true,false),closed:if(and(lte(provider_start_time_day,{current_time}),gte(provider_end_time_day,{current_time})),false,true),serviceability:if(lte(geodist(provider_geo),provider_service_location_distance),true,false),distance:geodist()',
        "sort": "geodist() asc",
        "sfield": "provider_geo",
        "pt": f"{lat},{lon}",
        "rows": rows_per_page,
        "start": start,
        "group": "true",
        "group.field": "provider_name_string",
        "group.sort": "geodist() asc",
        # "group.limit": 1,
        # "group.offset": start,
        # "group.ngroups": "true",
        "facet": "true",
        "facet.field": ["provider_status", "provider_name_string", "item_category_id"],
        "wt": "json",
    }
    if text_query == "*":
        params["q"] = (f"provider_name:{text_query}",)
    else:
        params["q"] = (f'provider_name:"{text_query}"^10',)
        params["q.knn"] = ([f"{{!knn f=provider_name_vector topK={vector_limit}}}{text_query_vector}"],)
    if type in SOLR_SELECT_URLS.keys():
        solr_url = SOLR_SELECT_URLS[type]
        results = await post_search_in_solr(solr_url, params)
        logger.debug(f"solr results {results}")
        final_response = [parse_final_providers_response(results, type)]
        return final_response
    else:
        urls = SOLR_SELECT_URLS.values()
        results = await asyncio.gather(*[post_search_in_solr(solr_url, params) for solr_url in urls])
        final_response = [parse_final_providers_response(result, type) for result, type in zip(results, SOLR_SELECT_URLS.keys(), strict=False)]
        return final_response


async def search_sub_categories(type: SearchTypesEnum, lat: float, lon: float, radius: int) -> Any:
    # filter_query=[]
    filter_query = [f"{{!geofilt sfield=provider_geo pt={lat},{lon} d={radius}}}"]
    # if filters["provider_status_filter"] is not None:
    #     filter_query.append(f"provider_status:{filters['provider_status_filter']}")
    # if filters["item_category_id_filter"] is not None:
    #     filter_query.append(f"item_category_id:{' OR '.join([f'"{name}"' for name in filters['item_category_id_filter']])}")
    # if filters["provider_names_filter"] is not None:
    #     filter_query.append(f"provider_name_string:{' OR '.join([f'"{name}"' for name in filters['provider_names_filter']])}")
    # if filters["verified_filter"] is not None and filters["verified_filter"] == "enable":
    #     filter_query.append(f"bpp_id:{' OR '.join(envConfig.trusted_bpps)}")
    # today: int = get_day_number()
    # current_time: int = get_current_time()

    # start = (page - 1) * rows_per_page
    # raw_vector = generate_text_embeddings(text_query)[0]
    # text_query_vector = "[" + ",".join(map(str, raw_vector.tolist())) + "]"
    # vector_limit = 1000
    params = {
        "defType": "edismax",
        "q": "*:*",
        "fq": filter_query,
        # "fl": f'id,domain,item_category_id,provider_name,provider_symbol,provider_status,provider_id,provider_geo,provider_location_city,provider_location_area_code,provider_location_street,provider_location_id,provider_min_order_value,provider_start_time_day,provider_end_time_day,provider_days,provider_service_location_distance,provider_service_type,provider_symbol,availability:if(query({{!v="provider_days:{today}"}}),true,false),closed:if(and(lte(provider_start_time_day,{current_time}),gte(provider_end_time_day,{current_time})),false,true),serviceability:if(lte(geodist(provider_geo),provider_service_location_distance),true,false),distance:geodist()',
        # "sort": "geodist() asc",
        # "sfield": "provider_geo",
        # "pt": f"{lat},{lon}",
        # "rows": rows_per_page,
        # "start": start,
        # "group": "true",
        # "group.field": "provider_name_string",
        # "group.sort": "geodist() asc",
        # "group.limit": 1,
        # "group.offset": start,
        # "group.ngroups": "true",
        "facet": "true",
        "facet.field": "item_category_id",
        "facet.sort": "count",
        "facet.mincount": 1,
        "facet.limit": -1,
        "rows": 0,
        "wt": "json",
    }
    if type in SOLR_SELECT_URLS.keys():
        solr_url = SOLR_SELECT_URLS[type]
        results = await post_search_in_solr(solr_url, params)
        logger.debug(f"solr results {results}")
        final_response = [parse_sub_categories_response(results, type)]
        return final_response
    else:
        urls = SOLR_SELECT_URLS.values()
        results = await asyncio.gather(*[post_search_in_solr(solr_url, params) for solr_url in urls])
        final_response = [parse_sub_categories_response(result, type) for result, type in zip(results, SOLR_SELECT_URLS.keys(), strict=False)]
        return final_response
