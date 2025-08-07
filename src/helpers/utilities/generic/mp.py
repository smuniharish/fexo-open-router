import asyncio
import logging
from multiprocessing.pool import Pool
from typing import Any

from src.helpers.utilities.generic.get_free_cpus import cpus_count

logger = logging.getLogger(__name__)


def create_pool() -> Pool:
    p = Pool(processes=cpus_count)
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
