import os
from dotenv import load_dotenv

load_dotenv()

mongo_uri = os.getenv("MONGODB_URL",None)
print("mongo_uri", mongo_uri)
mongo_auth_username = os.getenv("MONGO_AUTH_USERNAME",None)
print("mongo_auth_username",mongo_auth_username)
mongo_auth_password = os.getenv("MONGO_AUTH_PASSWORD",None)
print("mongo_auth_password",mongo_auth_password)
mongo_database_name =os.getenv("DATABASE_NAME",None)
print("mongo_database_name", mongo_database_name)
mongo_collection_name = os.getenv("COLLECTION_NAME",None)
print("mongo_collection_name", mongo_collection_name)
solr_base_url = os.getenv("SOLR_URL")
print("solr_base_url", solr_base_url)

def get_mongo_uri_env():
    return mongo_uri
def get_mongo_auth_username_env():
    return mongo_auth_username
def get_mongo_auth_password_env():
    return mongo_auth_password
def get_mongo_database_env():
    return mongo_database_name
def get_mongo_collection_env():
    return mongo_collection_name
def get_solr_base_uri_env():
    return solr_base_url