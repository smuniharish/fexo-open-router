from models.text_embeddings import generate_text_embeddings


def process_documents(document):
    try:
        summary = document.get("summary", {})
        if summary:
            item_symbol = str(summary.get("item_symbol", None))
            item_short_desc = summary.get("item_short_desc", "")
            item_long_desc = summary.get("item_long_desc", "")
            provider_location_lat = summary["provider_location"][1]
            provider_location_lang = summary["provider_location"][0]
            provider_geo = f"{provider_location_lat},{provider_location_lang}"
            item_name = summary.get("item_name", "")
            provider_name = summary.get("provider_name", None)
            item_name_vector = generate_text_embeddings(item_name).tolist()
            item_long_desc_vector = generate_text_embeddings(item_long_desc).tolist()
            item_short_desc_vector = generate_text_embeddings(item_short_desc).tolist()
            item_name_suggester_payload = f"{item_symbol} | item_name"
            provider_name_suggester_payload = f" | provider_name"
            doc = {
                "id": summary.get("_id", None),
                "code": summary.get("code", None),
                "domain": summary.get("domain", None),
                "bpp_id": summary.get("bpp_id", None),
                "bpp_name": summary.get("bpp_name", None),
                "bpp_uri": summary.get("bpp_uri", None),
                "city": summary.get("city", None),
                "item_id": summary.get("item_id", None),
                "item_offers": summary.get("item_offers", None),
                "parent_item_id": summary.get("parent_item_id", None),
                "item_category_id": summary.get("item_category_id", None),
                "item_currency": summary.get("item_currency", None),
                "item_measure_quantity": summary.get("item_measure_quantity", None),
                "item_measure_value": summary.get("item_measure_value", None),
                "item_name": item_name,
                "item_name_vector": item_name_vector,
                "item_short_desc": item_short_desc,
                "item_short_desc_vector": item_short_desc_vector,
                "item_long_desc": item_long_desc,
                "item_long_desc_vector": item_long_desc_vector,
                "item_name_suggester_payload": item_name_suggester_payload,
                "provider_name_suggester_payload": provider_name_suggester_payload,
                "item_selling_price": summary.get("item_selling_price", None),
                "item_mrp_price": summary.get("item_mrp_price", None),
                "item_discount_percentage": summary.get("item_discount_percentage", None),
                "item_status": summary.get("item_status", None),
                "item_timestamp": str(summary.get("item_timestamp", None)),
                "provider_timestamp": str(summary.get("provider_timestamp", None)),
                "item_symbol": item_symbol,
                "item_veg": summary["item_veg_or_nonveg"]["veg"],
                "item_nonveg": summary["item_veg_or_nonveg"]["non_veg"],
                "item_available_count": summary.get("item_available_count", None),
                "item_maximum_count": summary.get("item_maximum_count", None),
                "item_cancellable_status": summary.get("item_cancellable_status", None),
                "item_returnable_status": summary.get("item_returnable_status", None),
                "provider_name": provider_name,
                "provider_status": summary.get("provider_status", None),
                "provider_geo": provider_geo,
                "provider_id": summary.get("provider_id", None),
                "provider_location_id": summary.get("provider_location_id", None),
                "provider_location_city": summary.get("provider_location_city", None),
                "provider_location_area_code": summary.get("provider_location_area_code", None),
                "provider_location_street": summary.get("provider_location_street", None),
            }
            return doc
        return None
    except KeyError as e:
        print(f"KeyError: Missing key {e} in document {document}")
        return None
    except Exception as e:
        print(f"Exception: {e}")
        return None

def process_documents_without_vectors(document):
    try:
        summary = document.get("summary", {})
        if summary:
            item_symbol = str(summary.get("item_symbol", None))
            item_short_desc = summary.get("item_short_desc", "")
            item_long_desc = summary.get("item_long_desc", "")
            provider_location_lat = summary["provider_location"][1]
            provider_location_lang = summary["provider_location"][0]
            provider_geo = f"{provider_location_lat},{provider_location_lang}"
            item_name = summary.get("item_name", "")
            item_name_suggester_payload = f"{item_symbol} | item_name"
            provider_name_suggester_payload = f" | provider_name"
            # item_name_vector = generate_text_embeddings(item_name).tolist()
            # item_long_desc_vector = generate_text_embeddings(item_long_desc).tolist()
            # item_short_desc_vector = generate_text_embeddings(item_short_desc).tolist()
            doc = {
                "id": summary.get("_id", None),
                "code": summary.get("code", None),
                "domain": summary.get("domain", None),
                "bpp_id": summary.get("bpp_id", None),
                "bpp_name": summary.get("bpp_name", None),
                "bpp_uri": summary.get("bpp_uri", None),
                "city": summary.get("city", None),
                "item_id": summary.get("item_id", None),
                "item_offers": summary.get("item_offers", None),
                "parent_item_id": summary.get("parent_item_id", None),
                "item_category_id": summary.get("item_category_id", None),
                "item_currency": summary.get("item_currency", None),
                "item_measure_quantity": summary.get("item_measure_quantity", None),
                "item_measure_value": summary.get("item_measure_value", None),
                "item_name": item_name,
                # "item_name_vector": item_name_vector,
                "item_short_desc": item_short_desc,
                # "item_short_desc_vector": item_short_desc_vector,
                "item_long_desc": item_long_desc,
                # "item_long_desc_vector": item_long_desc_vector,
                "item_name_suggester_payload":item_name_suggester_payload,
                "provider_name_suggester_payload":provider_name_suggester_payload,
                "item_selling_price": summary.get("item_selling_price", None),
                "item_mrp_price": summary.get("item_mrp_price", None),
                "item_discount_percentage": summary.get("item_discount_percentage", None),
                "item_status": summary.get("item_status", None),
                "item_timestamp": str(summary.get("item_timestamp", None)),
                "provider_timestamp": str(summary.get("provider_timestamp", None)),
                "item_symbol": item_symbol,
                "item_veg": summary["item_veg_or_nonveg"]["veg"],
                "item_nonveg": summary["item_veg_or_nonveg"]["non_veg"],
                "item_available_count": summary.get("item_available_count", None),
                "item_maximum_count": summary.get("item_maximum_count", None),
                "item_cancellable_status": summary.get("item_cancellable_status", None),
                "item_returnable_status": summary.get("item_returnable_status", None),
                "provider_name": summary.get("provider_name", None),
                "provider_status": summary.get("provider_status", None),
                "provider_geo": provider_geo,
                "provider_id": summary.get("provider_id", None),
                "provider_location_id": summary.get("provider_location_id", None),
                "provider_location_city": summary.get("provider_location_city", None),
                "provider_location_area_code": summary.get("provider_location_area_code", None),
                "provider_location_street": summary.get("provider_location_street", None),
            }
            return doc
        return None
    except KeyError as e:
        print(f"KeyError: Missing key {e} in document {document}")
        return None
    except Exception as e:
        print(f"Exception: {e}")
        return None
