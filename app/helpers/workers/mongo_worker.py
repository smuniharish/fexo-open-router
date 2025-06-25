import asyncio
import logging
from typing import List, Optional

from app.database.mongodb import bulk_push_to_mongo
from app.helpers.Enums.mongo_status_enum import MongoStatusEnum
from app.helpers.TypedDicts.process_document_types import MongoValidDocsType
from app.helpers.utilities.envVar import envConfig
from app.helpers.utilities.get_free_cpus import get_free_cpus

logger = logging.getLogger(__name__)

MONGO_MAX_QUEUE_SIZE = envConfig.mongo_max_queue_size
MONGO_BATCH_SIZE = envConfig.mongo_batch_size
MONGO_BATCH_TIME = envConfig.mongo_batch_time
# Shared variables
queue: asyncio.Queue[MongoValidDocsType] = asyncio.Queue(maxsize=MONGO_MAX_QUEUE_SIZE)
batch: List[MongoValidDocsType] = []
batch_lock = asyncio.Lock()
shutdown_event = asyncio.Event()
mongo_worker_task: Optional[asyncio.Task] = None
mongo_flush_semaphore = asyncio.Semaphore(get_free_cpus())


async def mongo_worker() -> None:
    """Main Mongo batch processor: handles queue + timed batch flush."""
    logger.info("Mongo worker initialized")

    asyncio.create_task(flush_timer())

    while not shutdown_event.is_set():
        try:
            item = await asyncio.wait_for(queue.get(), timeout=1.0)
        except asyncio.TimeoutError:
            continue
        async with batch_lock:
            batch.append(item)
            if len(batch) >= MONGO_BATCH_SIZE:
                await flush_batch()


async def flush_timer() -> None:
    """Flushes batch every mongo_batch_time seconds regardless of size."""
    while not shutdown_event.is_set():
        await asyncio.sleep(MONGO_BATCH_TIME)
        async with batch_lock:
            if batch:
                await flush_batch()


async def add_to_mongo_queue(record: MongoValidDocsType) -> MongoValidDocsType:
    """Add a record to the queue, with backpressure if full."""
    while queue.full():
        logger.warning(f"Queue is full ({queue.qsize()}) - waiting to enqueue")
        await asyncio.sleep(2)
    await queue.put(record)
    return record


async def bulk_add_to_mongo_queue(records: List[MongoValidDocsType]) -> List[MongoValidDocsType]:
    """Add a record to the queue, with backpressure if full."""
    while queue.full():
        logger.warning(f"Queue is full ({queue.qsize()}) - waiting to enqueue")
        await asyncio.sleep(2)
    # await queue.put(record)
    await asyncio.gather(*(queue.put(doc) for doc in records))
    return records


# def sanitize_value(value: Any) -> Any:
#     if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
#         return None
#     elif isinstance(value, dict):
#         return {k: sanitize_value(v) for k, v in value.items()}
#     elif isinstance(value, list):
#         return [sanitize_value(v) for v in value]
#     return value


# def sanitize_record(record: ProcessDocumentType) -> ProcessDocumentType:
#     return cast(ProcessDocumentType, sanitize_value(record))


async def flush_batch() -> None:
    """Flush current batch to Mongo."""
    if not batch:
        return
    docs_to_send = batch.copy()
    try:
        # sanitized_batch = [sanitize_record(doc) for doc in docs_to_send]
        async with mongo_flush_semaphore:
            await bulk_push_to_mongo(docs_to_send, MongoStatusEnum.NEW)
        logger.info(f"Flushed {len(docs_to_send)} documents to Mongo")
    except Exception as e:
        logger.exception(f"Error flushing batch to mongo: {e}")
    finally:
        batch.clear()


# Startup & Shutdown handlers


async def start_mongo_worker() -> None:
    global mongo_worker_task
    mongo_worker_task = asyncio.create_task(mongo_worker())


async def stop_mongo_worker() -> None:
    shutdown_event.set()
    await asyncio.sleep(3)  # Let any pending flush_timer sleep finish
    async with batch_lock:
        if batch:
            await flush_batch()
    if mongo_worker_task:
        await mongo_worker_task
    logger.info("Mongo worker gracefully stopped.")
