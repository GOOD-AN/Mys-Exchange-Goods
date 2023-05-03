"""
初始化
"""
import logging.config

from apscheduler.events import EVENT_JOB_ADDED, EVENT_JOB_REMOVED, EVENT_JOB_MODIFIED, EVENT_JOB_MISSED, \
    EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import logging_config
from .global_var import GlobalVar


class Logger:
    """
    日志
    """

    def __init__(self):
        # 自定义日志路径与名称
        log_path = global_var.basic_path / 'log' / 'meg_all.log'
        if not log_path.parent.exists():
            log_path.parent.mkdir(parents=True, exist_ok=True)
        logging_config.log_config['handlers']['standard_file']['filename'] = log_path
        logging.config.dictConfig(logging_config.log_config)
        self.logger = logging.getLogger('info_file_logger')


def scheduler_log_listener(event):
    """
    监听基础定时任务事件(此处事件只会输出到日志)
    """
    try:
        if event.code == EVENT_JOB_ADDED:
            logger.info(f"任务 {event.job_id} 已添加")
        elif event.code == EVENT_JOB_REMOVED:
            logger.info(f"任务 {event.job_id} 已删除")
        elif event.code == EVENT_JOB_MODIFIED:
            logger.info(f"任务 {event.job_id} 已修改")
        elif event.code == EVENT_JOB_MISSED:
            logger.warning(f"任务 {event.job_id} 已错过")
        elif event.code == EVENT_JOB_ERROR:
            logger.error(f"任务 {event.job_id} 运行出错, 错误为: {event.exception}")
        elif event.code == EVENT_JOB_EXECUTED:
            logger.info(f"任务 {event.job_id} 已执行")
    except Exception as err:
        logger.error(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        return False


global_var = GlobalVar()
logger = Logger().logger
scheduler = AsyncIOScheduler({'apscheduler.timezone': 'Asia/Shanghai'})
scheduler.add_listener(scheduler_log_listener,
                       EVENT_JOB_ADDED | EVENT_JOB_REMOVED | EVENT_JOB_MODIFIED | EVENT_JOB_MISSED | EVENT_JOB_EXECUTED)

from .com_tool import async_input, check_update, init_config
from .mi_tool import check_cookie, update_cookie
from .get_info import info_menu
from .exchange_goods import init_exchange, wait_tasks
