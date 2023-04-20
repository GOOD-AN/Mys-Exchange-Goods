"""
初始化
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler({'apscheduler.timezone': 'Asia/Shanghai'})

from .com_tool import async_input, check_update, init_config
from .mi_tool import check_cookie, update_cookie
from .get_info import info_menu
from .exchange_goods import init_exchange, wait_tasks
