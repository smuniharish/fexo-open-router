import asyncio
import json
from asyncio import Semaphore
from datetime import datetime

import httpx

from app.helpers.utilities.Semaphore import network_semaphore

core = "ret_fnb"
source_solr_url = f"https://retail-buyer-solr.nearshop.in/solr/{core}/select"
target_url = "https://stagingondcfs.finfotech.co.in/ss/solr-index/"

BATCH_FETCH_SIZE = 10000
MAX_CONCURRENT_REQUESTS = 100


# Mapping one Solr doc to final schema
def transform_doc(doc):
    result = {
        "collection_type": "fnb",
        "id": doc.get("id", ""),
        "code": doc.get("code", ""),
        "domain": doc.get("domain", ""),
        "bpp_id": doc.get("bpp_id", ""),
        "bpp_name": doc.get("bpp_name", ""),
        "bpp_uri": doc.get("bpp_uri", ""),
        "city": doc.get("city", ""),
        "item_id": doc.get("item_id", ""),
        "item_offers": doc.get("item_offers", []),
        "parent_item_id": doc.get("parent_item_id", ""),
        "item_category_id": doc.get("item_category_id", ""),
        "item_currency": doc.get("item_currency", "INR"),
        "item_measure_quantity": doc.get("item_measure_quantity", "unit"),
        "item_measure_value": float(doc.get("item_measure_value", 0)),
        "item_name": doc.get("item_name", ""),
        "item_short_description": doc.get("item_short_desc", ""),
        "item_long_description": doc.get("item_long_desc", ""),
        "item_selling_price": float(doc.get("item_selling_price", 1)),
        "item_mrp_price": float(doc.get("item_mrp_price", 0)),
        "item_status": doc.get("item_status", "enable"),
        "item_timestamp": doc.get("item_timestamp", datetime.utcnow().isoformat()),
        "provider_timestamp": doc.get("provider_timestamp", datetime.utcnow().isoformat()),
        "item_symbol": doc.get("item_symbol", ""),
        "provider_symbol": doc.get("provider_symbol", ""),
        "item_veg": doc.get("item_veg", "true"),
        "item_nonveg": doc.get("item_nonveg", "true"),
        "item_discount_percentage": float(doc.get("item_discount_percentage", 0)),
        "item_available_count": int(doc.get("item_available_count", 0)),
        "item_maximum_count": int(doc.get("item_maximum_count", 0)),
        "item_cancellable_status": doc.get("item_cancellable_status", "enable"),
        "item_returnable_status": doc.get("item_returnable_status", "enable"),
        "provider_name": doc.get("provider_name", ""),
        "provider_status": doc.get("provider_status", "enable"),
        "provider_geo_latitude": float(doc.get("provider_geo_latitude", 0)),
        "provider_geo_longitude": float(doc.get("provider_geo_longitude", 0)),
        "provider_id": doc.get("provider_id", ""),
        "provider_location_id": doc.get("provider_location_id", ""),
        "provider_location_city": doc.get("provider_location_city", ""),
        "provider_location_area_code": doc.get("provider_location_area_code", ""),
        "provider_location_street": doc.get("provider_location_street", ""),
        "provider_min_order_value": float(doc.get("provider_min_order_value", 0)),
        "provider_start_time_day": int(doc.get("provider_start_time_day", 2359)),
        "provider_end_time_day": int(doc.get("provider_end_time_day", 2359)),
        "provider_days": doc.get("provider_days", []),
        "provider_service_location_distance": float(doc.get("provider_service_location_distance", 0)),
        "provider_service_type": int(doc.get("provider_service_type", 10)),
    }
    # print("result",result)
    return result


# Fetch 1000 documents from Solr
async def fetch_documents(start: int) -> list:
    params = {"q": "*:*", "start": start, "rows": BATCH_FETCH_SIZE, "wt": "json"}
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(source_solr_url, params=params)
        response.raise_for_status()
        return response.json()["response"]["docs"]


# Send single doc with concurrency control
# Send single doc with concurrency control and retry
failed_ids = []  # ← global list to collect all failed IDs
final_failed_payloads = []


async def send_single_doc(doc: dict, client: httpx.AsyncClient, sem: Semaphore):
    async with sem:
        payload = transform_doc(doc)

        for attempt in range(5):
            try:
                resp = await client.post(target_url, json=payload, timeout=30.0)
                resp.raise_for_status()
                print(f"✅ Sent: {payload.get('id')}")
                return
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                if attempt == 0:
                    print(f"⚠️ Failed {payload.get('id')} - retrying in 30s...")
                    await asyncio.sleep(30)
                else:
                    print(f"❌ Final fail {payload.get('id')}: {e}")
                    failed_ids.append(payload.get("id"))  # ← track this


async def retry_failed_documents_by_id(ids):
    if not ids:
        print("✅ No failed IDs to retry.")
        return

    print(f"\n🔁 Retrying {len(ids)} failed documents...")

    async with httpx.AsyncClient(verify=False) as client:
        for i in range(0, len(ids), 100):  # batch Solr query in chunks
            id_chunk = ids[i : i + 100]
            fq = " OR ".join([f"id:{json.dumps(iid)}" for iid in id_chunk])
            params = {"q": "*:*", "fq": fq, "rows": len(id_chunk), "wt": "json"}

            try:
                response = await client.get(source_solr_url, params=params)
                response.raise_for_status()
                docs = response.json()["response"]["docs"]
                print(f"🔄 Retrying {len(docs)} fetched from Solr")

                # Per-doc retry logic again
                tasks = []
                for doc in docs:
                    payload = transform_doc(doc)

                    async def retry_post(p=payload):  # closure to capture payload
                        for attempt in range(2):
                            try:
                                resp = await client.post(target_url, json=p, timeout=30.0)
                                resp.raise_for_status()
                                print(f"✅ Retried OK: {p['id']}")
                                return
                            except Exception as e:
                                if attempt == 0:
                                    print(f"⚠️ Retry failed {p['id']} once. Waiting 30s...")
                                    await asyncio.sleep(30)
                                else:
                                    print(f"❌ Retry FINAL fail {p['id']}: {e}")
                                    final_failed_payloads.append(p)  # ← collect failed payload here

                    tasks.append(retry_post())

                await asyncio.gather(*tasks)

            except Exception as e:
                print(f"❌ Error fetching retry batch from Solr: {e}")


# Process all docs in current Solr batch
async def send_docs_concurrently(docs: list):
    async with httpx.AsyncClient(verify=False) as client:
        tasks = [send_single_doc(doc, client, network_semaphore) for doc in docs]
        await asyncio.gather(*tasks)


# Overall transfer loop
async def transfer_all_documents():
    start = 0
    total = 0

    while True:
        print(f"\n📥 Fetching from offset: {start}")
        docs = await fetch_documents(start)
        if not docs:
            print("✅ All documents sent.")
            break

        print(f"📤 Sending {len(docs)} documents (50 at a time)...")
        await send_docs_concurrently(docs)

        total += len(docs)
        start += BATCH_FETCH_SIZE

    print(f"\n🎉 DONE! Total documents sent: {total}")
    # ⏱️ Wait 30 seconds before retrying failed documents
    if failed_ids:
        print(f"\n⏳ Waiting 30 seconds before retrying {len(failed_ids)} failed docs...")
        await asyncio.sleep(30)
        await retry_failed_documents_by_id(failed_ids)

    # ✅ Save final failed payloads only after retry
    if final_failed_payloads:
        output_file = f"failed_payloads_{core}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(final_failed_payloads, f, indent=2, ensure_ascii=False)
        print(f"\n📁 Final failed payloads written to: {output_file}")


if __name__ == "__main__":
    asyncio.run(transfer_all_documents())
