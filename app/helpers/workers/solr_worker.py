import asyncio
import logging
from typing import Any, List

from app.services.solr_db.solr_db_operations import batch_index_to_solr

logger = logging.getLogger(__name__)

BATCH_SIZE = 1000
BATCH_TIME = 5

queue: asyncio.Queue[Any] = asyncio.Queue()
batch: List[Any] = []
batch_lock = asyncio.Lock()


async def solr_worker() -> None:
    """Worker that process the queue based on batch size or time"""
    logger.info("solr worker initialized")
    global batch
    while True:
        await asyncio.sleep(BATCH_TIME)
        async with batch_lock:
            if len(batch) >= BATCH_SIZE or (batch and not queue.empty()):
                await batch_index_to_solr(batch)
                batch = []


async def add_to_queue(record: dict) -> Any:
    """Receive a record and queue it for batch indexing"""
    await queue.put(record)
    async with batch_lock:
        batch.append(record)

        if len(batch) >= BATCH_SIZE:
            await batch_index_to_solr(batch)
            batch.clear()
    return record
