from src.config.event_loop import configure_event_loop
configure_event_loop()

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Any

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import src.logging_setup  # noqa
from src.config.multiprocessing import configure_multiprocessing
from src.helpers.utilities.custom.yaml_config import load_yaml_configs
from src.config.orjson import ORJSONResponse
from src.helpers.utilities.custom.env_var import envConfig
from src.routers import health,chat

logger = logging.getLogger(__name__)

APP_IP = envConfig.app_ip
APP_PORT = envConfig.app_port
APP_RELOAD = envConfig.app_reload
APP_WORKERS = envConfig.app_workers
APP_DEBUG_LOGS_ENABLED = envConfig.debug_logs_enabled


@asynccontextmanager
async def lifespan(application: FastAPI) -> Any:
    logger.info("Configuring Multiprocessing workers...")
    configure_multiprocessing()
    logger.info("Multiprocessing workers Configured!")
    
    logger.info("Loading YAML Configs...")
    load_yaml_configs()
    logger.info("YAML Configs Loaded !")

    logger.info(f"Server started successfully at port {APP_PORT}")

    yield
    logger.info("Shutting down...")
    # await asyncio.gather()


description = """
OpenRouter AI (Fexo)
"""
app_server = FastAPI(
    title="Open Router AI",
    description=description,
    summary="Open Router, A single point destination to interact with LLMs",
    version="0.0.1",
    terms_of_service="http://dummy.com",
    contact={
        "name": "S MUNI HARISH",
        "url": "https://www.linkedin.com/in/smuniharish",
        "email": "samamuniharish@gmail.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
        "identifier": "Apache 2.0",
    },
    # root_path="/",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)
logger.info("Initializing Middlewares...")
app_server.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
logger.info("Middlewares Initialized")

logger.info("Initializing Routers...")
app_server.include_router(health.router)
app_server.include_router(chat.router)
logger.info("Routers Initialized")


def main() -> None:
    if APP_RELOAD:
        uvicorn.run("main:app_server", host=APP_IP, port=APP_PORT, reload=APP_RELOAD, workers=APP_WORKERS, reload_excludes=["logs/*", "*.log", "**/*.log"])
    else:
        uvicorn.run("main:app_server", host=APP_IP, port=APP_PORT, workers=APP_WORKERS)


if __name__ == "__main__":
    main()
