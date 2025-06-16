import logging
from typing import Any, List, Optional

from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import ValidationError
from pymongo import UpdateOne

from app.database.mongodb.pydantic import AddIndexFromMongoDb
from app.helpers.Enums import CollectionTypesEnum
from app.helpers.TypedDicts.process_document_types import ProcessDocumentType
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


async def get_source_documents(collection_type: CollectionTypesEnum, limit: int, skip: int) -> Any:
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
    query = {"indexed": False}
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


async def get_non_indexed_documents() -> Any:
    if not mongo_client:
        raise Exception("MongoDB client is not initialized.")
    db = mongo_client[MONGO_DATABASE_NAME]
    collection = db[MONGO_COLLECTION_PROCESSED]
    query = {"indexed": False}
    docs = []
    projection = {"_id": 0, "indexed": 0}
    async for doc in collection.find(query, projection).limit(1000):
        docs.append(doc)
    return docs


async def update_indexed_field(doc_ids: list) -> Any:
    if not mongo_client:
        raise Exception("MongoDB client is not initialized.")
    db = mongo_client[MONGO_DATABASE_NAME]
    collection = db[MONGO_COLLECTION_PROCESSED]

    filter_query = {"_id": {"$in": doc_ids}}
    update_query = {"$set": {"indexed": True}}

    try:
        result = await collection.update_many(filter_query, update_query)
        logger.info(f"Updated {result.modified_count} documents to 'indexed: true'.")
        return {"message": f"Updated {result.modified_count} documents to 'indexed: true'."}
    except Exception as e:
        logger.error(f"Error updating indexed field: {e}")
        return {"error": str(e)}


async def bulk_push_to_mongo(items: List[ProcessDocumentType]) -> Any:
    if not mongo_client:
        raise Exception("MongoDB client is not initialized.")
    db = mongo_client[MONGO_DATABASE_NAME]
    collection = db[MONGO_COLLECTION_PROCESSED]

    operations = [UpdateOne(filter={"_id": item["doc"]["id"]}, update={"$set": {**item, "_id": item["doc"]["id"], "indexed": False}}, upsert=True) for item in items]

    try:
        result = await collection.bulk_write(operations, ordered=False)
        logger.info(f"Updated {result.modified_count} documents to 'indexed: true'.")
        return {"message": f"Updated {result.modified_count} documents to 'indexed: true'."}
    except Exception as e:
        logger.error(f"Error updating indexed field: {e}")
        return {"error": str(e)}
