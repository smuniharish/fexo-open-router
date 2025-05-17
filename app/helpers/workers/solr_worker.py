import asyncio
import logging
import math
from typing import Any, Dict, List, Optional

from app.helpers.utilities.envVar import envConfig
from app.services.solr_db.solr_db_operations import batch_index_to_solr

logger = logging.getLogger(__name__)

queue: asyncio.Queue[Any] = asyncio.Queue(maxsize=envConfig.solr_max_queue_size)
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
            if len(batch) >= envConfig.solr_batch_size:
                await flush_batch()


async def flush_timer() -> None:
    """Flushes batch every BATCH_TIME seconds regardless of size."""
    while True:
        await asyncio.sleep(envConfig.solr_batch_time)
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


def sanitize_record(record: Dict[str, Any]) -> Dict[str, Optional[Any]]:
    def sanitize_value(value: Any) -> Optional[Any]:
        if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
            return None  # or a default value like 0.0
        return value

    return {k: sanitize_value(v) for k, v in record.items()}


async def flush_batch() -> None:
    """Flush current batch to Solr."""
    if not batch:
        return
    docs_to_send = batch.copy()
    try:
        sanitized_batch = [sanitize_record(doc) for doc in docs_to_send]
        await batch_index_to_solr(sanitized_batch)
        logger.info(f"Flushed {len(docs_to_send)} documents to Solr")
    except Exception as e:
        logger.exception(f"Error flushing batch: {e}")
    finally:
        batch.clear()
