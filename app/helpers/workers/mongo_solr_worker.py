import asyncio
import logging
from typing import List, Optional

from app.helpers.TypedDicts.process_document_types import ProcessDocumentType
from app.helpers.utilities.envVar import envConfig
from app.helpers.utilities.get_free_cpus import cpus_count
from app.helpers.workers.solr_worker import add_to_solr_queue
from app.services.solr.solr_service import process_new_stored_docs

logger = logging.getLogger(__name__)

MONGO_SOLR_MAX_QUEUE_SIZE = envConfig.mongo_solr_max_queue_size
MONGO_SOLR_BATCH_SIZE = envConfig.mongo_solr_batch_size
MONGO_SOLR_BATCH_TIME = envConfig.mongo_solr_batch_time
MONGO_SOLR_FETCH_INTERVAL = envConfig.mongo_solr_batch_time
# Shared variables
queue: asyncio.Queue[ProcessDocumentType] = asyncio.Queue(maxsize=MONGO_SOLR_MAX_QUEUE_SIZE)
batch: List[ProcessDocumentType] = []
batch_lock = asyncio.Lock()
shutdown_event = asyncio.Event()
mongo_solr_worker_task: Optional[asyncio.Task] = None
mongo_solr_flush_semaphore = asyncio.Semaphore(cpus_count)


async def mongo_solr_worker() -> None:
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
            if len(batch) >= MONGO_SOLR_BATCH_SIZE:
                await flush_batch()


async def flush_timer() -> None:
    """Flushes batch every mongo_solr_batch_time seconds regardless of size."""
    while not shutdown_event.is_set():
        await asyncio.sleep(MONGO_SOLR_BATCH_TIME)
        async with batch_lock:
            if batch:
                await flush_batch()


async def fetch_to_mongo_solr_queue() -> None:
    logger.info("Starting periodic fetcher for NEW Status documents")

    while not shutdown_event.is_set():
        if queue.full():
            logger.debug("Queue is full, skipping fetch cycle")
        else:
            try:
                async with mongo_solr_flush_semaphore:
                    records = await process_new_stored_docs()
                # records = await process_new_stored_docs()
                remaining_capacity = queue.maxsize - queue.qsize()
                records = records[:remaining_capacity]  # enforce queue limit

                for record in records:
                    await queue.put(record)
                logger.info(f"Fetched and queued {len(records)} records")

            except Exception as e:
                logger.exception(f"Error fetching NEW STATUS documents: {e}")

        await asyncio.sleep(MONGO_SOLR_FETCH_INTERVAL)


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
    """Flush current batch to Solr Queue."""
    if not batch:
        return
    docs_to_send = batch.copy()
    try:
        # sanitized_batch = [sanitize_record(doc) for doc in docs_to_send]
        async with mongo_solr_flush_semaphore:
            await asyncio.gather(*(add_to_solr_queue(doc) for doc in docs_to_send))
        logger.info(f"Flushed {len(docs_to_send)} documents to Solr Queue")
    except Exception as e:
        logger.exception(f"Error flushing batch to solr queue: {e}")
    finally:
        batch.clear()


# Startup & Shutdown handlers


async def start_mongo_solr_worker() -> None:
    global mongo_solr_worker_task
    mongo_solr_worker_task = asyncio.create_task(mongo_solr_worker())
    asyncio.create_task(fetch_to_mongo_solr_queue())


async def stop_mongo_solr_worker() -> None:
    shutdown_event.set()
    await asyncio.sleep(3)  # Let any pending flush_timer sleep finish
    async with batch_lock:
        if batch:
            await flush_batch()
    if mongo_solr_worker_task:
        await mongo_solr_worker_task
    logger.info("Mongo worker gracefully stopped.")
