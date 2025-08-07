import asyncio
from typing import Any

from src.helpers.utilities.generic.mp import create_process_in_pool
from src.helpers.utilities.generic.thread_pool import thread_executor


async def run_process_thread_pool_async(func: Any, args: Any) -> Any:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(thread_executor, create_process_in_pool, func, args)
