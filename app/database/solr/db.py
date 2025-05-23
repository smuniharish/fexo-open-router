from typing import Optional

import httpx

from app.helpers.utilities.envVar import envConfig

SOLR_MAX_CONNECTIONS = envConfig.solr_max_connections
SOLR_MAX_KEEPALIVE_CONNECTIONS = envConfig.solr_max_keepalive_connections
SOLR_KEEP_ALIVE_EXPIRY = envConfig.solr_keep_alive_expiry

_client: Optional[httpx.AsyncClient] = None


def load_solr_client() -> httpx.AsyncClient:
    global _client
    if _client is None:
        _client = httpx.AsyncClient(limits=httpx.Limits(max_connections=SOLR_MAX_CONNECTIONS, max_keepalive_connections=SOLR_MAX_KEEPALIVE_CONNECTIONS, keepalive_expiry=SOLR_KEEP_ALIVE_EXPIRY))
    return _client


async def close_solr_client() -> None:
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None


def get_solr_client() -> httpx.AsyncClient | None:
    return _client
