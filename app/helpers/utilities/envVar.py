import logging
import os
from typing import List

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
    def debug_logs_enabled(self) -> bool:
        return eval(os.getenv("DEBUG_LOGS_ENABLED", "False"))

    @property
    def mongo_uri(self) -> str:
        return os.getenv("MONGODB_URL", "127.0.0.1:27017")

    @property
    def mongo_auth_username(self) -> str | None:
        return os.getenv("MONGO_AUTH_USERNAME", None)

    @property
    def mongo_auth_password(self) -> str | None:
        return os.getenv("MONGO_AUTH_PASSWORD", None)

    @property
    def mongo_auth_source(self) -> str | None:
        return os.getenv("MONGO_AUTH_SOURCE", None)

    @property
    def mongo_auth_mechanism(self) -> str | None:
        return os.getenv("MONGO_AUTH_MECHANISM", None)

    @property
    def mongo_database_name(self) -> str:
        return os.getenv("MONGO_DATABASE_NAME", "")

    @property
    def mongo_collection_grocery(self) -> str:
        return os.getenv("MONGO_COLLECTION_GROCERY", "")

    @property
    def mongo_collection_fnb(self) -> str:
        return os.getenv("MONGO_COLLECTION_FNB", "")

    @property
    def mongo_collection_electronics(self) -> str:
        return os.getenv("MONGO_COLLECTION_ELECTRONICS", "")

    @property
    def mongo_collection_processed(self) -> str:
        return os.getenv("MONGO_COLLECTION_PROCESSED", "")

    @property
    def solr_base_url(self) -> str:
        return os.getenv("SOLR_BASE_URL", "")

    @property
    def solr_grocery_core(self) -> str:
        return os.getenv("SOLR_GROCERY_CORE", "")

    @property
    def solr_fnb_core(self) -> str:
        return os.getenv("SOLR_FNB_CORE", "")

    @property
    def solr_electronics_core(self) -> str:
        return os.getenv("SOLR_ELECTRONICS_CORE", "")

    @property
    def solr_max_connections(self) -> int:
        return int(os.getenv("SOLR_MAX_CONNECTIONS", 10000000))

    @property
    def solr_max_keepalive_connections(self) -> int:
        return int(os.getenv("SOLR_MAX_KEEPALIVE_CONNECTIONS", 10000))

    @property
    def solr_keep_alive_expiry(self) -> int:
        return int(os.getenv("SOLR_KEEP_ALIVE_EXPIRY", 100))

    @property
    def solr_max_queue_size(self) -> int:
        return int(os.getenv("SOLR_MAX_QUEUE_SIZE", 100000))

    @property
    def solr_batch_size(self) -> int:
        return int(os.getenv("SOLR_BATCH_SIZE", 100))

    @property
    def solr_batch_time(self) -> int:
        return int(os.getenv("SOLR_BATCH_TIME", 5))

    @property
    def mongo_max_queue_size(self) -> int:
        return int(os.getenv("MONGO_MAX_QUEUE_SIZE", 100000))

    @property
    def mongo_batch_size(self) -> int:
        return int(os.getenv("MONGO_BATCH_SIZE", 100))

    @property
    def mongo_batch_time(self) -> int:
        return int(os.getenv("MONGO_BATCH_TIME", 5))

    @property
    def mongo_solr_max_queue_size(self) -> int:
        return int(os.getenv("MONGO_SOLR_MAX_QUEUE_SIZE", 100000))

    @property
    def mongo_solr_batch_size(self) -> int:
        return int(os.getenv("MONGO_SOLR_BATCH_SIZE", 100))

    @property
    def mongo_solr_batch_time(self) -> int:
        return int(os.getenv("MONGO_SOLR_BATCH_TIME", 5))

    @property
    def mongo_solr_fetch_interval(self) -> int:
        return int(os.getenv("MONGO_SOLR_FETCH_INTERVAL", 5))

    @property
    def trusted_bpps(self) -> List[str]:
        return os.getenv("TRUSTED_BPPS", "").split(",")


envConfig = EnvConfig()
