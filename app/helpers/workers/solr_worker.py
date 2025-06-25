import asyncio
import logging
import math
from typing import Any, List, Optional, cast

from app.helpers.TypedDicts.process_document_types import ProcessDocumentType
from app.helpers.utilities.envVar import envConfig
from app.helpers.utilities.get_free_cpus import cpus_count
from app.services.solr_db.solr_db_operations import batch_index_to_solr

logger = logging.getLogger(__name__)

SOLR_MAX_QUEUE_SIZE = envConfig.solr_max_queue_size
SOLR_BATCH_SIZE = envConfig.solr_batch_size
SOLR_BATCH_TIME = envConfig.solr_batch_time
# Shared variables
queue: asyncio.Queue[ProcessDocumentType] = asyncio.Queue(maxsize=SOLR_MAX_QUEUE_SIZE)
batch: List[ProcessDocumentType] = []
batch_lock = asyncio.Lock()
shutdown_event = asyncio.Event()
solr_worker_task: Optional[asyncio.Task] = None
solr_flush_semaphore = asyncio.Semaphore(cpus_count)


async def solr_worker() -> None:
    """Main solr batch processor: handles queue + timed batch flush."""
    logger.info("Solr worker initialized")

    asyncio.create_task(flush_timer())

    while not shutdown_event.is_set():
        try:
            item = await asyncio.wait_for(queue.get(), timeout=1.0)
        except asyncio.TimeoutError:
            continue
        async with batch_lock:
            batch.append(item)
            if len(batch) >= SOLR_BATCH_SIZE:
                await flush_batch()


async def flush_timer() -> None:
    """Flushes batch every solr_batch_time seconds regardless of size."""
    while not shutdown_event.is_set():
        await asyncio.sleep(SOLR_BATCH_TIME)
        async with batch_lock:
            if batch:
                await flush_batch()


async def add_to_solr_queue(record: ProcessDocumentType) -> ProcessDocumentType:
    """Add a record to the queue, with backpressure if full."""
    while queue.full():
        logger.warning(f"Queue is full ({queue.qsize()}) - waiting to enqueue")
        await asyncio.sleep(2)
    await queue.put(record)
    return record


def sanitize_value(value: Any) -> Any:
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    elif isinstance(value, dict):
        return {k: sanitize_value(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [sanitize_value(v) for v in value]
    return value


def sanitize_record(record: ProcessDocumentType) -> ProcessDocumentType:
    return cast(ProcessDocumentType, sanitize_value(record))


async def flush_batch() -> None:
    """Flush current batch to Solr."""
    if not batch:
        return
    docs_to_send = batch.copy()
    try:
        sanitized_batch = [sanitize_record(doc) for doc in docs_to_send]
        async with solr_flush_semaphore:
            await batch_index_to_solr(sanitized_batch)
        logger.info(f"Flushed {len(docs_to_send)} documents to Solr")
    except Exception as e:
        logger.exception(f"Error flushing batch: {e}")
    finally:
        batch.clear()


# Startup & Shutdown handlers


async def start_solr_worker() -> None:
    global solr_worker_task
    solr_worker_task = asyncio.create_task(solr_worker())


async def stop_solr_worker() -> None:
    shutdown_event.set()
    await asyncio.sleep(3)  # Let any pending flush_timer sleep finish
    async with batch_lock:
        if batch:
            await flush_batch()
    if solr_worker_task:
        await solr_worker_task
    logger.info("Solr worker gracefully stopped.")
