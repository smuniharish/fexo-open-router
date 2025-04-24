import asyncio
import logging
from multiprocessing import Pool
from typing import Any

from app.helpers.utilities.get_free_cpus import get_free_cpus

logger = logging.getLogger(__name__)


def create_pool() -> Any:
    freecpusLength = len(get_free_cpus())
    logger.info(f"server having free cpus::{freecpusLength}")
    free_cpus = freecpusLength
    p = Pool(free_cpus)
    return p


def create_process_in_pool(process_func: Any, args: Any) -> Any:
    try:
        p = create_pool()
        results = p.map(process_func, args)
        p.close()
        p.join()
        return results
    except Exception as e:
        logger.error(f"Error in creating process in pool: {e}")


# Function to process documents asynchronously in parallel
async def process_in_parallel(func: Any, args: Any) -> Any:
    # Create a list of tasks for all documents
    tasks = [asyncio.create_task(func(doc)) for doc in args]
    # Await all tasks concurrently
    results = await asyncio.gather(*tasks)
    return results


def create_process_in_async_pool(process_func: Any, args: Any) -> Any:
    try:

        def wrapper(doc: Any) -> Any:
            return asyncio.run(process_func(doc))

        p = create_pool()
        results = p.map_async(wrapper, args)
        p.close()
        p.join()
        return results.get()
    except Exception as e:
        logger.error(f"Error in creating process in pool: {e}")


def create_process_in_starmap_async_pool(process_func: Any, args: Any) -> Any:
    try:
        p = create_pool()
        results = p.starmap_async(process_func, args)
        p.close()
        p.join()
        return results
    except Exception as e:
        logger.error(f"Error in creating process in pool: {e}")


def create_process_in_starmap_pool(process_func: Any, args: Any) -> Any:
    try:
        p = create_pool()
        results = p.starmap(process_func, args)
        p.close()
        p.join()
        return results
    except Exception as e:
        logger.error(f"Error in creating process in pool: {e}")
