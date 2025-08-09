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
    def debug_logs_enabled(self) -> bool:
        return eval(os.getenv("DEBUG_LOGS_ENABLED", "False"))

    @property
    def openai_secret_key(self) -> str | None:
        return os.getenv("OPENAI_SECRET_KEY", None)

    @property
    def azure_openai_secret_key(self) -> str | None:
        return os.getenv("AZURE_OPENAI_SECRET_KEY", None)

    @property
    def anthropic_secret_key(self) -> str | None:
        return os.getenv("ANTHROPIC_SECRET_KEY", None)

    @property
    def google_secret_key(self) -> str | None:
        return os.getenv("GOOGLE_SECRET_KEY", None)

    @property
    def xyzcloud_secret_key(self) -> str | None:
        return os.getenv("XYZCLOUD_SECRET_KEY", None)

    @property
    def partnerai_secret_key(self) -> str | None:
        return os.getenv("PARTNERAI_SECRET_KEY", None)


envConfig = EnvConfig()
