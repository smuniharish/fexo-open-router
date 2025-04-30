import asyncio
import logging
from typing import Any, List
import math

from app.services.solr_db.solr_db_operations import batch_index_to_solr

logger = logging.getLogger(__name__)

BATCH_SIZE = 1000
BATCH_TIME = 5
MAX_QUEUE_SIZE = 100_000

queue: asyncio.Queue[Any] = asyncio.Queue(maxsize=MAX_QUEUE_SIZE)
batch: List[Any] = []
batch_lock = asyncio.Lock()


async def solr_worker() -> None:
    """Main solr batch processor: handles queue + timed batch flush."""
    logger.info("Solr worker initialized")

    # Start flush timer loop
    asyncio.create_task(flush_timer())

    while True:
        item = await queue.get()
        async with batch_lock:
            batch.append(item)
            if len(batch) >= BATCH_SIZE:
                await flush_batch()


async def flush_timer() -> None:
    """Flushes batch every BATCH_TIME seconds regardless of size."""
    while True:
        await asyncio.sleep(BATCH_TIME)
        async with batch_lock:
            if batch:
                await flush_batch()


async def add_to_queue(record: dict) -> Any:
    """Add a record to the queue, with backpressure if full."""
    while queue.full():
        logger.warning(f"Queue is full ({queue.qsize()}) - waiting to enqueue")
        await asyncio.sleep(2)

    await queue.put(record)
    return record

def sanitize_record(record: dict) -> dict:
    def sanitize_value(value):
        if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
            return None  # or a default value like 0.0
        return value

    return {k: sanitize_value(v) for k, v in record.items()}

async def flush_batch() -> None:
    """Flush current batch to Solr."""
    if not batch:
        return

    try:
        sanitized_batch = [sanitize_record(doc) for doc in batch.copy()]
        await batch_index_to_solr(sanitized_batch)
        logger.info(f"Flushed {len(batch)} documents to Solr")
    except Exception as e:
        logger.exception(f"Error flushing batch: {e}")
    finally:
        batch.clear()
