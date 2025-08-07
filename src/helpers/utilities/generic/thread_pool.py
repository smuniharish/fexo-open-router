from concurrent.futures import ThreadPoolExecutor

from src.helpers.utilities.generic.get_free_cpus import cpus_count

thread_executor = ThreadPoolExecutor(max_workers=cpus_count)
