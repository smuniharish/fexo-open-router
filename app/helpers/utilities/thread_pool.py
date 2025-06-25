from concurrent.futures import ThreadPoolExecutor

from app.helpers.utilities.get_free_cpus import cpus_count
thread_executor = ThreadPoolExecutor(max_workers=cpus_count)