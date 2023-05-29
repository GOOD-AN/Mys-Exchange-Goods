"""
cli通用函数
"""
import asyncio
from apscheduler.events import EVENT_JOB_ADDED, EVENT_JOB_REMOVED, EVENT_JOB_MODIFIED, EVENT_JOB_MISSED, \
    EVENT_JOB_EXECUTED
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from ..com_tool import scheduler_log_listener


async def async_input(prompt=''):
    """
    异步输入
    """
    try:
        return await asyncio.to_thread(input, prompt)
    except AttributeError:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, input, prompt)


scheduler = AsyncIOScheduler({'apscheduler.timezone': 'Asia/Shanghai'})
scheduler.add_listener(scheduler_log_listener,
                       EVENT_JOB_ADDED | EVENT_JOB_REMOVED | EVENT_JOB_MODIFIED | EVENT_JOB_MISSED | EVENT_JOB_EXECUTED)
