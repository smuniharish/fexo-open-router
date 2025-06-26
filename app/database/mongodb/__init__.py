import logging
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Any, Mapping, Optional, Sequence,List, Dict

from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import ValidationError
from pymongo import UpdateOne

from app.database.mongodb.pydantic import AddIndexFromMongoDb
from app.helpers.Enums import CollectionTypesEnum
from app.helpers.Enums.mongo_status_enum import MongoStatusEnum
from app.helpers.utilities.envVar import envConfig

logger = logging.getLogger(__name__)

MONGO_URL = envConfig.mongo_uri
MONGO_AUTH_USERNAME = envConfig.mongo_auth_username
MONGO_AUTH_PASSWORD = envConfig.mongo_auth_password
MONGO_AUTH_SOURCE = envConfig.mongo_auth_source
MONGO_AUTH_MECHANISM = envConfig.mongo_auth_mechanism
MONGO_DATABASE_NAME = envConfig.mongo_database_name

MONGO_COLLECTION_GROCERY = envConfig.mongo_collection_grocery
MONGO_COLLECTION_FNB = envConfig.mongo_collection_fnb
MONGO_COLLECTION_ELECTRONICS = envConfig.mongo_collection_electronics
MONGO_COLLECTION_PROCESSED = envConfig.mongo_collection_processed

mongourl = f"mongodb://{MONGO_URL}"
if MONGO_AUTH_USERNAME and MONGO_AUTH_PASSWORD:
    mongourl = f"mongodb://{MONGO_AUTH_USERNAME}:{MONGO_AUTH_PASSWORD}@{MONGO_URL}"
    if MONGO_AUTH_SOURCE:
        mongourl += f"?authSource={MONGO_AUTH_SOURCE}"
    if MONGO_AUTH_MECHANISM:
        mongourl += f"&authMechanism=${MONGO_AUTH_MECHANISM}"
logger.info(f"final mongourl:{mongourl}")

mongo_client: Optional[AsyncIOMotorClient] = None


def load_mongo_client() -> AsyncIOMotorClient:
    global mongo_client
    if mongo_client is None:
        mongo_client = AsyncIOMotorClient(mongourl)
    return mongo_client


async def close_mongo_client() -> None:
    global mongo_client
    if mongo_client:
        mongo_client.close()
        mongo_client = None


async def get_source_documents(collection_type: CollectionTypesEnum, limit: int, skip: int, status: str) -> Any:
    if collection_type == CollectionTypesEnum.GROCERY:
        collection_name = MONGO_COLLECTION_GROCERY
    elif collection_type == CollectionTypesEnum.FNB:
        collection_name = MONGO_COLLECTION_FNB
    else:
        collection_name = MONGO_COLLECTION_ELECTRONICS
    if not mongo_client:
        raise Exception("MongoDB client is not initialized.")
    db = mongo_client[MONGO_DATABASE_NAME]
    collection = db[collection_name]
    query = {"STATUS": status}
    valid_docs = []
    invalid_docs = []
    projection = {"_id": 0}
    async for doc in collection.find(query, projection).limit(limit).skip(skip):
        try:
            extracted_doc = AddIndexFromMongoDb(**doc)
            valid_docs.append(extracted_doc)
        except ValidationError as e:
            invalid_docs.append({"doc": doc, "error": str(e)})

    logger.debug("==========invalid documents=======")
    logger.debug(len(invalid_docs))
    if len(invalid_docs):
        logger.warning(invalid_docs)
    logger.debug("=====valid documents======")
    logger.debug(len(valid_docs))
    return valid_docs


async def get_documents_with_status(status: str) -> Any:
    if not mongo_client:
        raise Exception("MongoDB client is not initialized.")
    db = mongo_client[MONGO_DATABASE_NAME]
    collection = db[MONGO_COLLECTION_PROCESSED]
    query = {"STATUS": status}
    docs = []
    projection = {"STATUS": 0}
    async for doc in collection.find(query, projection).limit(1000):
        docs.append(doc)
    return docs


async def update_status_field_with_ids(doc_ids: list, status: str, error: Optional[str] = None) -> Any:
    if not mongo_client:
        raise Exception("MongoDB client is not initialized.")
    db = mongo_client[MONGO_DATABASE_NAME]
    collection = db[MONGO_COLLECTION_PROCESSED]

    now = datetime.now(timezone.utc)

    filter_query = {"_id": {"$in": doc_ids}}
    update_query = {"$set": {"STATUS": status, "updatedAt": now}}
    if error:
        update_query["$set"]["error"] = error

    try:
        result = await collection.update_many(filter_query, update_query)
        logger.info(f"Updated {result.modified_count} documents to STATUS:{status}.")
        return {"message": f"Updated {result.modified_count} documents to STATUS:{status}."}
    except Exception as e:
        logger.error(f"Error updating STATUS field: {e}")
        return {"error": str(e)}


async def update_queued_to_new() -> Any:
    if not mongo_client:
        raise Exception("MongoDB client is not initialized.")
    db = mongo_client[MONGO_DATABASE_NAME]
    collection = db[MONGO_COLLECTION_PROCESSED]

    now = datetime.now(timezone.utc)

    filter_query = {"STATUS": MongoStatusEnum.QUEUED}
    update_query = {"$set": {"STATUS": MongoStatusEnum.NEW, "updatedAt": now}}

    try:
        result = await collection.update_many(filter_query, update_query)
        logger.info(f"Updated {result.modified_count} documents to 'STATUS: {MongoStatusEnum.NEW}'.")
        return {"message": f"Updated {result.modified_count} documents to 'STATUS: {MongoStatusEnum.NEW}'."}
    except Exception as e:
        logger.error(f"Error updating STATUS field: {e}")
        return {"error": str(e)}


async def bulk_push_to_mongo(items: list[Any], status: str) -> Any:
    if not mongo_client:
        raise Exception("MongoDB client is not initialized.")

    db = mongo_client[MONGO_DATABASE_NAME]
    collection = db[MONGO_COLLECTION_PROCESSED]
    now = datetime.now(timezone.utc)

    def clean_for_mongo(data: dict) -> dict:
        def convert(value: Any) -> Any:
            if isinstance(value, Decimal):
                return float(value)
            elif isinstance(value, Enum):
                return value.value
            elif isinstance(value, dict):
                return clean_for_mongo(value)
            elif isinstance(value, list):
                return [convert(v) for v in value]
            return value

        return {k: convert(v) for k, v in data.items()}

    operations = []
    for item in items:
        doc_obj = item["doc"]  # This is the Pydantic model
        doc_dict = clean_for_mongo(doc_obj.model_dump())  # Convert to plain dict (for Pydantic v2)
        doc_id = doc_obj.id  # Safe access

        # Merge fields to update in Mongo
        update_doc = {
            **item,  # includes 'collection_type'
            "doc": doc_dict,  # serialize doc properly
            "_id": doc_id,
            "STATUS": status,
            "updatedAt": now,
        }

        op = UpdateOne(filter={"_id": doc_id}, update={"$set": update_doc, "$setOnInsert": {"createdAt": now}}, upsert=True)
        operations.append(op)

    try:
        result = await collection.bulk_write(operations, ordered=False)
        logger.info(f"Updated {result.modified_count} documents to db")
        return {"message": f"Updated {result.modified_count} documents to db"}
    except Exception as e:
        logger.error(f"Error updating STATUS field: {e}")
        return {"error": str(e)}


async def get_documents_count_with_status(status: str) -> Any:
    if not mongo_client:
        raise Exception("MongoDB client is not initialized.")

    db = mongo_client[MONGO_DATABASE_NAME]
    collection = db[MONGO_COLLECTION_PROCESSED]

    pipeline: Sequence[Mapping[str, Any]] = [
        {"$match": {
            "STATUS": status,
            "collection_type": {"$in": ["grocery", "electronics", "fnb"]}
        }},
        {"$group": {"_id": "$collection_type", "count": {"$sum": 1}}}
    ]

    results = []
    async for doc in collection.aggregate(pipeline):
        results.append(doc)

    return results

async def fetch_documents_by_status_and_time(
    status: str,
    start_time: Optional[str],
    end_time: Optional[str]
) -> List[Dict[str, Any]]:
    if not mongo_client:
        raise Exception("MongoDB client is not initialized.")

    db = mongo_client[MONGO_DATABASE_NAME]
    collection = db[MONGO_COLLECTION_PROCESSED]

    # Base query
    query: Dict[str, Any] = {
        "STATUS": status,
        "collection_type": {"$in": ["grocery", "electronics", "fnb"]}
    }

    # Add time range filter if provided
    if start_time or end_time:
        time_filter: Dict[str, Any] = {}
        if start_time:
            time_filter["$gte"] = datetime.fromisoformat(start_time)
        if end_time:
            time_filter["$lte"] = datetime.fromisoformat(end_time)
        query["createdAt"] = time_filter

    cursor = collection.find(query)

    docs = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        if "createdAt" in doc:
            doc["createdAt"] = doc["createdAt"].isoformat()
        if "updatedAt" in doc:
            doc["updatedAt"] = doc["updatedAt"].isoformat()
        docs.append(doc)

    return docs