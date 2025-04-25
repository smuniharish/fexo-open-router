import asyncio
import logging
import logging.config
from contextlib import asynccontextmanager
from typing import Any

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.logging_config import LOGGING_CONFIG
from app.config.orjsonConfig import ORJSONResponse
from app.database.solr.db import close_client, get_client
from app.helpers.utilities.envVar import envConfig
from app.helpers.workers.solr_worker import solr_worker
from app.routers import discovery, health, initial_index_from_db, solr_index

logging.config.dictConfig(LOGGING_CONFIG)


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(application: FastAPI) -> Any:
    logger.info("Initializing Solr client...")
    get_client()
    logger.info("Starting Solr worker...")
    asyncio.create_task(solr_worker())
    yield
    await close_client()


description = """
Solr Search API helps you do awesome stuff. 🚀
"""
app = FastAPI(
    title="Search System (PROD)",
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
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
logger.info("Middlewares Initialized")

logger.info("Initializing Routers...")
app.include_router(health.router)
app.include_router(solr_index.router)
app.include_router(discovery.router)
app.include_router(initial_index_from_db.router)
logger.info("Routers Initialized")


def main() -> None:
    uvicorn.run("main:app", host=envConfig.app_ip, port=envConfig.app_port, reload=envConfig.app_reload, workers=envConfig.app_workers, reload_excludes=["logs/*", "*.log", "**/*.log"])


if __name__ == "__main__":
    main()
