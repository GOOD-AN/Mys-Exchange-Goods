"""
初始化
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler({'apscheduler.timezone': 'Asia/Shanghai'})
scheduler.start()

from .com_tool import async_input, check_update, init_config
from .get_info import info_menu
