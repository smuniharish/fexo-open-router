from motor.motor_asyncio import AsyncIOMotorClient

from functions.pydantic_models import ItemDocument
from pydantic import ValidationError

from helpers.env_constants import get_mongo_uri_env, get_mongo_database_env, get_mongo_collection_env, \
    get_mongo_auth_username_env, get_mongo_auth_password_env

MONGODB_URL = get_mongo_uri_env()
MONGODB_AUTH_USERNAME = get_mongo_auth_username_env()
MONGODB_AUTH_PASSWORD = get_mongo_auth_password_env()
DATABASE_NAME = get_mongo_database_env()
COLLECTION_NAME = get_mongo_collection_env()

async def get_source_documents(limit,skip):
    mongourl = f"mongodb://{MONGODB_URL}"
    if MONGODB_AUTH_USERNAME is not None and MONGODB_AUTH_PASSWORD is not None:
        mongourl = f"mongodb://{MONGODB_AUTH_USERNAME}:{MONGODB_AUTH_PASSWORD}@{MONGODB_URL}"
    client = AsyncIOMotorClient(mongourl)
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]
    valid_docs = []
    invalid_docs = []
    query = {}
    projection = {
        "_id": 0,
        "summary": 1
    }
    async for doc in collection.find(query, projection).limit(limit).skip(skip):
        try:
            extracted_doc = ItemDocument(**doc)
            valid_docs.append(extracted_doc.model_dump())
        except ValidationError as e:
            invalid_docs.append({"doc": doc, "error": str(e)})

    print("=======invalid documents=======")
    print(len(invalid_docs))
    print("======valid documents======")
    print(len(valid_docs))
    return valid_docs