from typing import Optional

import httpx

from app.helpers.utilities.envVar import envConfig

_client: Optional[httpx.AsyncClient] = None


def get_client() -> httpx.AsyncClient:
    global _client
    if _client is None:
        _client = httpx.AsyncClient(limits=httpx.Limits(max_connections=envConfig.solr_max_connections, max_keepalive_connections=envConfig.solr_max_keepalive_connections, keepalive_expiry=envConfig.solr_keep_alive_expiry))
    return _client


async def close_client() -> None:
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None
