import app.logging_setup  # noqa
import logging
from contextlib import asynccontextmanager
from typing import Any
import asyncio
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.orjsonConfig import ORJSONResponse
from app.database.solr.db import load_solr_client, close_solr_client
from app.helpers.circuit_breakers.solr_circuit_client import start_circuit_http_client, stop_circuit_http_client
from app.helpers.utilities.envVar import envConfig
from app.helpers.workers.solr_worker import start_solr_worker, stop_solr_worker
from app.routers import discovery, health, initial_index_from_db, solr_index
from app.database.mongodb import load_mongo_client, close_mongo_client

logger = logging.getLogger(__name__)

APP_IP = envConfig.app_ip
APP_PORT = envConfig.app_port
APP_RELOAD = envConfig.app_reload
APP_WORKERS = envConfig.app_workers
APP_DEBUG_LOGS_ENABLED = envConfig.debug_logs_enabled


@asynccontextmanager
async def lifespan(application: FastAPI) -> Any:
    logger.info("Initializing MongoDB client...")
    load_mongo_client()
    logger.info("Initializing Solr client...")
    load_solr_client()
    logger.info("Starting Solr worker and retry queue...")
    await asyncio.gather(start_solr_worker(), start_circuit_http_client())

    yield
    logger.info("Shutting down...")
    await asyncio.gather(close_mongo_client(), close_solr_client(), stop_solr_worker(), stop_circuit_http_client())


description = """
Solr Search API helps you do awesome stuff. 🚀
"""
app_server = FastAPI(
    title="Search System",
    description=description,
    summary="Search System project",
    version="0.0.1",
    terms_of_service="http://dummy.com",
    contact={
        "name": "Fast Api Starter",
        "url": "http://x-force.example.com/contact/",
        "email": "email@gmail.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
        "identifier": "MIT",
    },
    root_path="/ss",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)
logger.info("Initializing Middlewares...")
app_server.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
logger.info("Middlewares Initialized")

logger.info("Initializing Routers...")
app_server.include_router(health.router)
app_server.include_router(solr_index.router)
app_server.include_router(discovery.router)
app_server.include_router(initial_index_from_db.router)
logger.info("Routers Initialized")


def main() -> None:
    if APP_RELOAD:
        uvicorn.run("main:app_server", host=APP_IP, port=APP_PORT, reload=APP_RELOAD, workers=APP_WORKERS, reload_excludes=["logs/*", "*.log", "**/*.log"])
    else:
        uvicorn.run("main:app_server", host=APP_IP, port=APP_PORT, workers=APP_WORKERS)


if __name__ == "__main__":
    main()
