import asyncio
import logging
from typing import Any, List

from app.services.solr_db.solr_db_operations import batch_index_to_solr

logger = logging.getLogger(__name__)

BATCH_SIZE = 1000
BATCH_TIME = 5
MAX_QUEUE_SIZE = 100000

queue: asyncio.Queue[Any] = asyncio.Queue(maxsize=MAX_QUEUE_SIZE)
batch: List[Any] = []
batch_lock = asyncio.Lock()


async def solr_worker() -> None:
    """Worker that process the queue based on batch size or time"""
    logger.info("solr worker initialized")
    while True:
        try:
            item = await asyncio.wait_for(queue.get(),timeout=BATCH_TIME)
            async with batch_lock:
                batch.append(item)
                if len(batch) >= BATCH_SIZE:
                    await batch_index_to_solr(batch)
                    batch.clear()
        except asyncio.TimeoutError:
            async with batch_lock:
                if batch:
                    await batch_index_to_solr(batch)
                    batch.clear()


async def add_to_queue(record: dict) -> Any:
    """Receive a record and queue it for batch indexing"""
    while queue.full():
        logger.warning(f"Queue is full :: {queue.qsize()}, waiting...")
        await asyncio.sleep(2)
    await queue.put(record)
    return record
