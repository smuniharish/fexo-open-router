import asyncio

from app.helpers.utilities.mp import create_process_in_pool
from app.helpers.utilities.thread_pool import thread_executor


async def run_process_thread_pool_async(func, args):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(thread_executor, create_process_in_pool, func, args)
