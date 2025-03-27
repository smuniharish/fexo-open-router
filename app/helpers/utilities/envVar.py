import logging
import os

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

env = os.getenv("ENV", "development")
env_file = f".env.{env}"

load_dotenv(env_file)

print(f"loaded env print {env_file}")


class EnvConfig:
    @property
    def app_ip(self) -> str:
        return os.getenv("APP_IP", "0.0.0.0")

    @property
    def app_port(self) -> int:
        return int(os.getenv("APP_PORT", "3030"))

    @property
    def app_reload(self) -> bool:
        return eval(os.getenv("APP_RELOAD", "True"))

    @property
    def app_workers(self) -> int:
        return int(os.getenv("APP_WORKERS", "1"))

    @property
    def mongo_db_uri(self) -> str:
        return os.getenv("MONGODB_URL", "")

    @property
    def mongo_db_username(self) -> str:
        return os.getenv("MONGO_AUTH_USERNAME", "")

    @property
    def mongo_db_user_password(self) -> str:
        return os.getenv("MONGO_AUTH_PASSWORD", "")

    @property
    def mongo_db_name(self) -> str:
        return os.getenv("DATABASE_NAME", "")

    @property
    def mongo_db_collection_name(self) -> str:
        return os.getenv("COLLECTION_NAME", "")

    @property
    def solr_base_url(self) -> str:
        return os.getenv("SOLR_URL", "")

    @property
    def solr_base_url_v3(self) -> str:
        return os.getenv("SOLR_URL_V3", "")

    @property
    def solr_max_connections(self) -> int:
        return int(os.getenv("SOLR_MAX_CONNECTIONS", 10000000))

    @property
    def solr_max_keepalive_connections(self) -> int:
        return int(os.getenv("SOLR_MAX_KEEPALIVE_CONNECTIONS", 10000))

    @property
    def solr_keep_alive_expiry(self) -> int:
        return int(os.getenv("SOLR_KEEP_ALIVE_EXPIRY", 100))


envConfig = EnvConfig()
