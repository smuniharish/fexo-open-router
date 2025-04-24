import logging
from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import ValidationError

from app.database.mongodb.pydantic import AddIndexFromMongoDb
from app.helpers.utilities.envVar import envConfig

logger = logging.getLogger(__name__)

MONGO_URL = envConfig.mongo_db_uri
MONGO_AUTH_USERNAME = envConfig.mongo_db_username
MONGO_AUTH_PASSWORD = envConfig.mongo_db_password
DATABASE_NAME = envConfig.mongo_db_name
COLLECTION_NAME = envConfig.mongo_db_collection_name

mongourl = f"mongodb://{MONGO_URL}"
if MONGO_AUTH_USERNAME and MONGO_AUTH_PASSWORD:
    mongourl = f"mongodb://{MONGO_AUTH_USERNAME}:{MONGO_AUTH_PASSWORD}@{MONGO_URL}"
logger.info(f"final mongourl:{mongourl}")
client: AsyncIOMotorClient = AsyncIOMotorClient(mongourl)


async def get_source_documents(limit: int, skip: int) -> Any:
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]
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


async def update_indexed_field(doc_ids: list) -> Any:
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]

    filter_query = {"_id": {"$in": doc_ids}}
    update_query = {"$set": {"indexed": True}}

    try:
        result = await collection.update_many(filter_query, update_query)
        logger.info(f"Updated {result.modified_count} documents to 'indexed: true'.")
        return {"message": f"Updated {result.modified_count} documents to 'indexed: true'."}
    except Exception as e:
        logger.error(f"Error updating indexed field: {e}")
        return {"error": str(e)}
