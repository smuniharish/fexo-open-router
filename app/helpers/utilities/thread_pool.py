from concurrent.futures import ThreadPoolExecutor

from app.helpers.utilities.get_free_cpus import get_free_cpus
cpu_count = len(get_free_cpus())
thread_executor = ThreadPoolExecutor(max_workers=cpu_count)