import logging
import time
from concurrent.futures import as_completed
from typing import Any

import httpx
import schedule

from app.helpers.utilities.envVar import envConfig
from app.helpers.utilities.thread_pool import thread_executor

logger = logging.getLogger(__name__)

# --- Configuration ---
SOLR_BASE_URL = envConfig.solr_base_url
CORES = [
    envConfig.solr_grocery_core,
    envConfig.solr_electronics_core,
    envConfig.solr_fnb_core,
]
MAX_RETRIES = 2
RETRY_DELAY = 30


def optimize_core(core_name: str) -> Any:
    url = f"{SOLR_BASE_URL}{core_name}/update?optimize=true&maxSegments=1"
    try:
        with httpx.Client(timeout=None) as client:
            response = client.get(url)
            if response.status_code == 200:
                return True, f"Optimized {core_name}"
            else:
                return False, f"Error {response.status_code} optimizing {core_name}"
    except Exception as e:
        return False, f"Exception optimizing {core_name}: {e}"


def optimize_all_cores_with_retries() -> None:
    remaining_cores = list(CORES)
    attempt = 1

    while attempt <= MAX_RETRIES and remaining_cores:
        logger.info(f"\nAttempt {attempt}: Optimizing {remaining_cores}")
        failed_cores = []

        futures = {thread_executor.submit(optimize_core, core): core for core in remaining_cores}
        for future in as_completed(futures):
            success, message = future.result()
            logger.info(message)
            if not success:
                failed_cores.append(futures[future])

        if failed_cores:
            logger.warning(f"Failed cores: {failed_cores}")
            if attempt < MAX_RETRIES:
                logger.warning(f"Retrying in {RETRY_DELAY} sec...")
                time.sleep(RETRY_DELAY)
            remaining_cores = failed_cores
            attempt += 1
        else:
            break

    if remaining_cores:
        logger.warning(f"Final retry failed for: {remaining_cores}")
    else:
        logger.info("All cores optimized successfully!")


def _solr_scheduler_loop_blocking() -> None:
    schedule.every().day.at("00:05").do(optimize_all_cores_with_retries)
    schedule.every().day.at("12:05").do(optimize_all_cores_with_retries)

    logger.info("Solr Optimization Scheduler started. Will optimize Solr cores at 12 AM and 12 PM daily.")

    while True:
        schedule.run_pending()
        time.sleep(30)


def run_solr_optimization_scheduler() -> None:
    thread_executor.submit(_solr_scheduler_loop_blocking)
