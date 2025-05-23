import asyncio
import logging
from typing import Any, Dict, Optional, Tuple

from aiobreaker import CircuitBreaker
from httpx import Response  # Assuming you're using httpx

from app.database.solr.db import get_solr_client

logger = logging.getLogger(__name__)


class CircuitHttpClient:
    def __init__(self, failure_threshold: int = 3, recovery_timeout: int = 20, max_retries: int = 5, retry_delay: int = 5) -> None:
        self.breaker: CircuitBreaker = CircuitBreaker(fail_max=failure_threshold, timeout_duration=recovery_timeout)
        self.retry_queue: asyncio.Queue[Tuple[str, str, Dict[str, Any]]] = asyncio.Queue()
        self.max_retries: int = max_retries
        self.retry_delay: int = retry_delay
        self._retry_task: Optional[asyncio.Task] = None
        self._stop: bool = False

    async def start(self) -> None:
        """Start the background retry worker."""
        if self._retry_task is None:
            self._stop = False
            self._retry_task = asyncio.create_task(self._retry_worker())

    async def close(self) -> None:
        """Gracefully stop the background retry worker."""
        self._stop = True
        if self._retry_task:
            await self._retry_task

    async def request(self, method: str, url: str, **kwargs: Any) -> Response:
        logger.debug(f"Request passing from circuit client: {method} {url}")
        return await self.breaker.call(self._request_with_retries, method, url, **kwargs)

    async def _request_with_retries(self, method: str, url: str, **kwargs: Any) -> Response:
        client = get_solr_client()
        if not client:
            raise Exception("Solr client is not initialized.")
        logger.debug(f"Starting retries for {method} {url}")
        for attempt in range(1, self.max_retries + 1):
            logger.debug(f"Attempt #{attempt} for {method} {url}")
            try:
                response: Response = await client.request(method, url, **kwargs)
                response.raise_for_status()
                logger.debug(f"✅ Success on attempt {attempt} with status {response.status_code}")
                return response
            except Exception as exc:
                logger.error(f"❌ Attempt {attempt} failed: {exc}")
                if attempt == self.max_retries:
                    logger.warning("⚠️ Max retries reached. Queuing request.")
                    await self.retry_queue.put((method, url, kwargs))
                else:
                    logger.debug(f"Sleeping {self.retry_delay} seconds before next attempt")
                    await asyncio.sleep(self.retry_delay)
        raise Exception("All retries failed")  # Fallback in case the function exits without returning

    async def _retry_worker(self) -> None:
        while not self._stop:
            if self.breaker.current_state.name == "CLOSED" and not self.retry_queue.empty():
                logger.debug("📦 Circuit breaker closed. Retrying failed requests...")
                while not self.retry_queue.empty():
                    method, url, kwargs = await self.retry_queue.get()
                    try:
                        await self.breaker.call(self._request_with_retries, method, url, **kwargs)
                    except Exception as e:
                        logger.debug(f"🔁 Retry failed again: {e}")
            await asyncio.sleep(1)


circuit_http_client = CircuitHttpClient()


async def start_circuit_http_client() -> None:
    await circuit_http_client.start()


async def stop_circuit_http_client() -> None:
    await circuit_http_client.close()
