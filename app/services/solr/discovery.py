import asyncio
from typing import Any

from app.helpers.models.text_embeddings import generate_text_embeddings
from app.helpers.utilities.envVar import envConfig
from app.services.solr_db.solr_db_operations import post_search_in_solr


async def search_item_name_suggester(text_query: str, lat: float | None, lon: float | None, radius: int | None) -> Any:
    try:
        filter_query = []
        if lat and lon and radius is not None:
            filter_query.append(f"{{!geofilt sfield=provider_geo pt={lat},{lon} d = {radius}}}")
        params = {"defType": "edismax", "q": f'item_name:("{text_query}"^20) OR item_name_suggest:("{text_query}*"^10 OR "{text_query}"^5 OR "{text_query}"~1)', "fl": "id,suggest:item_name_suggest,text:item_name,payload:item_name_suggester_payload_string", "fq": filter_query, "hl": "true", "hl.fl": "item_name_suggest", "hl.simple.pre": "<b>", "hl.simple.post": "</b>", "group": "true", "group.field": "item_name_suggest", "group.limit": "1"}
        if lat and lon and radius is not None:
            params["sfield"] = "provider_geo"
            params["pt"] = f"{lat},{lon}"
        solr_url = envConfig.solr_base_url + "/select"
        results = await post_search_in_solr(solr_url, params)
        print("solr results", results)
        grouped_item_name_suggest = results.get("grouped", {}).get("item_name_suggest", {})
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
                    if doc_id in highlighting and "item_name_suggest" in highlighting[doc_id]:
                        doc["suggest"] = highlighting[doc_id]["item_name_suggest"][0]

                # Create a flat response structure
                flat_response = {
                    # "responseHeader": results.get("responseHeader", {}),
                    "response": {"numFound": len(flat_docs), "matches": matches, "start": 0, "docs": flat_docs}
                }
                return flat_response
            else:
                # No matching documents
                flat_response = {
                    # "responseHeader": results.get("responseHeader", {}),
                    "response": {"numFound": 0, "matches": 0, "start": 0, "docs": []}
                }
                return flat_response
        else:
            # No matching documents
            flat_response = {
                # "responseHeader": results.get("responseHeader", {}),
                "response": {"numFound": 0, "matches": 0, "start": 0, "docs": []}
            }
            return flat_response
    except Exception as e:
        print("excetion search_item_name_suggester", str(e))


async def search_provider_name_suggester(text_query: str, lat: float | None, lon: float | None, radius: int | None) -> Any:
    try:
        filter_query = []
        if lat and lon and radius is not None:
            filter_query.append(f"{{!geofilt sfield=provider_geo pt={lat},{lon} d = {radius}}}")
        params = {"defType": "edismax", "q": f'item_name:("{text_query}"^20) OR provider_name_suggest:("{text_query}*"^10 OR "{text_query}"^5 OR "{text_query}"~1)', "fl": "id,suggest:provider_name_suggest,text:provider_name,payload:provider_name_suggester_payload_string", "fq": filter_query, "hl": "true", "hl.fl": "provider_name_suggest", "hl.simple.pre": "<b>", "hl.simple.post": "</b>", "group": "true", "group.field": "provider_name_suggest", "group.limit": "1"}
        if lat and lon and radius is not None:
            params["sfield"] = "provider_geo"
            params["pt"] = f"{lat},{lon}"
        solr_url = envConfig.solr_base_url + "/select"
        results = await post_search_in_solr(solr_url, params)
        print("solr results", results)
        grouped_provider_name_suggest = results.get("grouped", {}).get("provider_name_suggest", {})
        if grouped_provider_name_suggest:
            grouped_data = grouped_provider_name_suggest.get("groups", [])
            matches = grouped_provider_name_suggest.get("matches", 0)
            # Check if there are any matching documents
            if grouped_data:
                flat_docs = [group["doclist"]["docs"][0] for group in grouped_data]

                # Merge highlighting into the docs section
                highlighting = results.get("highlighting", {})
                for doc in flat_docs:
                    doc_id = doc.get("id")
                    if doc_id in highlighting and "provider_name_suggest" in highlighting[doc_id]:
                        doc["suggest"] = highlighting[doc_id]["provider_name_suggest"][0]

                # Create a flat response structure
                flat_response = {
                    # "responseHeader": results.get("responseHeader", {}),
                    "response": {"numFound": len(flat_docs), "matches": matches, "start": 0, "docs": flat_docs}
                }
                return flat_response
            else:
                # No matching documents
                flat_response = {
                    # "responseHeader": results.get("responseHeader", {}),
                    "response": {"numFound": 0, "matches": 0, "start": 0, "docs": []}
                }
                return flat_response
    except Exception as e:
        print("excetion search_provider_name_suggester", str(e))


async def search_provider_item_name_suggest(text_query: str, lat: float | None, lon: float | None, radius: int | None) -> Any:
    item_suggest, provider_suggest = await asyncio.gather(search_item_name_suggester(text_query, lat, lon, radius), search_provider_name_suggester(text_query, lat, lon, radius))
    final_response = {"item_suggest": item_suggest["response"], "provider_suggest": provider_suggest["response"]}
    return final_response


async def search_item_name_with_vectors(text_query: str, lat: float, lon: float, radius: int, page: int, rows_per_page: int, sorting_value: str, filters: Any) -> Any:
    sorting_dict = {"RELEVANCE": None, "DISTANCE_HIGH_TO_LOW": "geodist() desc", "DISTANCE_LOW_TO_HIGH": "geodist() asc", "PRICE_HIGH_TO_LOW": "item_selling_price desc", "PRICE_LOW_TO_HIGH": "item_selling_price asc"}
    print("sorting value", sorting_value)
    print("filters", filters)
    # filter_query=[]
    filter_query = [f"{{!geofilt sfield=provider_geo pt={lat},{lon} d = {radius}}}"]
    if filters["provider_status_filter"] is not None:
        filter_query.append(f"provider_status:{filters['provider_status_filter']}")
    if filters["item_status_filter"] is not None:
        filter_query.append(f"item_status:{filters['item_status_filter']}")
    if filters["domains_filter"] is not None:
        final_domains_list = [domain.replace(":", "\\:") for domain in filters["domains_filter"]]
        filter_query.append(f"domain_string:{' OR '.join(final_domains_list)}")
    if filters["item_category_id_filter"] is not None:
        final_item_cat_list = [item_cat.replace(":", "\\:") for item_cat in filters["item_category_id_filter"]]
        filter_query.append(f"item_category_id:{' OR '.join(final_item_cat_list)}")
    if filters["provider_names_filter"] is not None:
        filter_query.append(f"provider_name_string:{' OR '.join(filters['provider_names_filter'])}")
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
        "q": f'item_name:"{text_query}"^10 OR item_short_desc:{text_query}^2 OR item_long_desc:{text_query}^1 ' + f"OR {{!knn f=item_name_vector topK={vector_limit}}}{text_query_vector}^3 " + f"OR {{!knn f=item_short_desc_vector topK={vector_limit}}}{text_query_vector}^2 " + f"OR {{!knn f=item_long_desc_vector topK={vector_limit}}}{text_query_vector}^1",
        # f"AND {{!geofilt sfield=provider_geo pt={lat},{lon} d={radius}}}",
        "fq": filter_query,
        "fl": "id,domain,bpp_id,city,item_id,item_currency,item_measure_quantity,item_measure_value,item_name,item_short_desc,item_long_desc,item_selling_price,item_mrp_price,item_discount_price,item_status,item_symbol,item_available_count,item_maximum_count,provider_name,provider_status,provider_geo,provider_id,provider_geo,provider_location_city,provider_location_area_code,provider_location_street,item_veg,distance:geodist()",
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
        "facet.field": ["provider_status", "item_status", "domain_string", "provider_name_string"],
        # "facet.pivot": "item_name_string,provider_name_string",
        "group": "true",
        "group.field": "item_name_string",
        "group.sort": "item_selling_price asc",
        # "group.limit": rows_per_page,
        # "group.offset": start,
        # "group.ngroups": "true",
        "wt": "json",
    }
    solr_url = envConfig.solr_base_url + "/select"
    results = await post_search_in_solr(solr_url, params)
    print("solr results", results)
    final_response = {"grouped": results["grouped"], "filters": results["facet_counts"]}
    return final_response


async def search_item_name_string_with_vectors(text_query: str, lat: float, lon: float, radius: int, page: int, rows_per_page: int, sorting_value: str, filters: Any) -> Any:
    sorting_dict = {"RELEVANCE": None, "DISTANCE_HIGH_TO_LOW": "geodist() desc", "DISTANCE_LOW_TO_HIGH": "geodist() asc", "PRICE_HIGH_TO_LOW": "item_selling_price desc", "PRICE_LOW_TO_HIGH": "item_selling_price asc"}
    print("sorting value", sorting_value)
    print("filters", filters)
    # filter_query = []
    filter_query = [f"{{!geofilt sfield=provider_geo pt={lat},{lon} d = {radius}}}"]
    if filters["provider_status_filter"] is not None:
        filter_query.append(f"provider_status:{filters['provider_status_filter']}")
    if filters["item_status_filter"] is not None:
        filter_query.append(f"item_status:{filters['item_status_filter']}")
    if filters["domains_filter"] is not None:
        final_domains_list = [domain.replace(":", "\\:") for domain in filters["domains_filter"]]
        filter_query.append(f"domain_string:{' OR '.join(final_domains_list)}")
    if filters["item_category_id_filter"] is not None:
        final_item_cat_list = [item_cat.replace(":", "\\:") for item_cat in filters["item_category_id_filter"]]
        filter_query.append(f"item_category_id:{' OR '.join(final_item_cat_list)}")
    if filters["provider_names_filter"] is not None:
        filter_query.append(f"provider_name_string:{' OR '.join(filters['provider_names_filter'])}")
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
        "q": f'item_name:"{text_query}"^10' + f"OR {{!knn f=item_name_vector topK={vector_limit}}}{text_query_vector}^3 " + f"OR {{!knn f=item_short_desc_vector topK={vector_limit}}}{text_query_vector}^2 " + f"OR {{!knn f=item_long_desc_vector topK={vector_limit}}}{text_query_vector}^1",
        # f"AND {{!geofilt sfield=provider_geo pt={lat},{lon} d={radius}}}",
        "fq": filter_query,
        "fl": "id,domain,bpp_id,city,item_id,item_currency,item_measure_quantity,item_measure_value,item_name,item_short_desc,item_long_desc,item_selling_price,item_mrp_price,item_discount_price,item_status,item_symbol,item_available_count,item_maximum_count,provider_name,provider_status,provider_geo,provider_id,provider_geo,provider_location_city,provider_location_area_code,provider_location_street,item_veg,distance:geodist()",
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
        "facet.field": ["provider_status", "item_status", "domain_string", "provider_name_string"],
        # "facet.pivot": "item_name_string,provider_name_string",
        # "group": "true",
        # "group.field": "item_name_string",
        # "group.sort":"item_selling_price asc",
        # "group.limit": rows_per_page,
        # "group.offset": start,
        # "group.ngroups": "true",
        "wt": "json",
    }
    solr_url = envConfig.solr_base_url + "/select"
    results = await post_search_in_solr(solr_url, params)
    print("solr results", results)
    final_response = {"response": results["response"], "filters": results["facet_counts"]}
    return final_response
