import asyncio

import psutil

from src.helpers.utilities.generic.get_free_cpus import cpus_count


def is_cpu_overloaded(threshold: int = 80) -> bool:
    """Returns True if overall CPU usage is above the threshold %."""
    return psutil.cpu_percent(interval=1) > threshold


def get_safe_io_limit(base_multiplier: int = 15, max_limit: int = 1000) -> int:
    """Dynamically calculates semaphore limit based on CPU usage."""
    if is_cpu_overloaded():
        adjusted = int(cpus_count * (base_multiplier / 2))
    else:
        adjusted = cpus_count * base_multiplier
    return min(adjusted, max_limit)


cpu_semaphore = asyncio.Semaphore(cpus_count)
disk_semaphore = asyncio.Semaphore(get_safe_io_limit(base_multiplier=15, max_limit=200))
network_semaphore = asyncio.Semaphore(get_safe_io_limit(base_multiplier=30, max_limit=400))
