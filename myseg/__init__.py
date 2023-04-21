"""
初始化
"""
from apscheduler.events import EVENT_JOB_ADDED, EVENT_JOB_REMOVED, EVENT_JOB_MODIFIED, EVENT_JOB_MISSED, \
    EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
from apscheduler.schedulers.asyncio import AsyncIOScheduler


def scheduler_log_listener(event):
    """
    监听基础定时任务事件(此处事件只会输出到日志)
    """
    try:
        if event.code == EVENT_JOB_ADDED:
            print(f"任务 {event.job_id} 已添加")
        elif event.code == EVENT_JOB_REMOVED:
            print(f"任务 {event.job_id} 已删除")
        elif event.code == EVENT_JOB_MODIFIED:
            print(f"任务 {event.job_id} 已修改")
        elif event.code == EVENT_JOB_MISSED:
            print(f"任务 {event.job_id} 已错过")
        elif event.code == EVENT_JOB_ERROR:
            print(f"任务 {event.job_id} 运行出错, 错误为: {event.exception}")
        elif event.code == EVENT_JOB_EXECUTED:
            print(f"任务 {event.job_id} 已执行")
    except Exception as err:
        print(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        return False


scheduler = AsyncIOScheduler({'apscheduler.timezone': 'Asia/Shanghai'})
scheduler.add_listener(scheduler_log_listener,
                       EVENT_JOB_ADDED | EVENT_JOB_REMOVED | EVENT_JOB_MODIFIED | EVENT_JOB_MISSED | EVENT_JOB_EXECUTED)

from .com_tool import async_input, check_update, init_config
from .mi_tool import check_cookie, update_cookie
from .get_info import info_menu
from .exchange_goods import init_exchange, wait_tasks
