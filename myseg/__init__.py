"""
初始化
"""
import json
import logging.config
import platform
import sys

from apscheduler.events import EVENT_JOB_ADDED, EVENT_JOB_REMOVED, EVENT_JOB_MODIFIED, EVENT_JOB_MISSED, \
    EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import logging_config
from .global_var import GlobalVar
from .user_data import GameInfo, AddressInfo, UserInfo


class Logger:
    """
    日志
    """

    def __init__(self, log_control, user_log_path=None):
        # 自定义日志路径与名称
        log_path = user_global_var.basic_path / 'log' / 'meg_all.log'
        if user_log_path:
            log_path = user_log_path
        if not log_path.parent.exists():
            log_path.parent.mkdir(parents=True, exist_ok=True)
        logging_config.log_config['handlers']['standard_file']['filename'] = log_path
        logging.config.dictConfig(logging_config.log_config)
        self.logger = logging.getLogger(log_control)


def scheduler_log_listener(event):
    """
    监听基础定时任务事件(此处事件只会输出到日志)
    """
    try:
        if event.code == EVENT_JOB_ADDED:
            logger_file.info(f"任务 {event.job_id} 已添加")
        elif event.code == EVENT_JOB_REMOVED:
            logger_file.info(f"任务 {event.job_id} 已删除")
        elif event.code == EVENT_JOB_MODIFIED:
            logger_file.info(f"任务 {event.job_id} 已修改")
        elif event.code == EVENT_JOB_MISSED:
            logger_file.warning(f"任务 {event.job_id} 已错过")
        elif event.code == EVENT_JOB_ERROR:
            logger_file.error(f"任务 {event.job_id} 运行出错, 错误为: {event.exception}")
        elif event.code == EVENT_JOB_EXECUTED:
            logger_file.info(f"任务 {event.job_id} 已执行")
    except Exception as err:
        logger.error(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        return False


def check_plat():
    """
    检查平台
    """
    try:
        if platform.system() == "Windows":
            return "cls"
        return "clear"
    except KeyboardInterrupt:
        logger.warning("用户强制退出")
        input("按回车键继续")
        sys.exit()
    except Exception as err:
        logger.error(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        input("按回车键继续")
        sys.exit()


def load_user_data():
    """
    加载用户数据
    """
    try:
        user_data_dict = {}
        if user_global_var.user_data_path.exists():
            user_data_file_list = user_global_var.user_data_path.iterdir()
            for user_data_file in user_data_file_list:
                logger.debug(user_data_file)
                with open(user_data_file, 'r', encoding='utf-8') as f:
                    try:
                        user_data_load = json.load(f)
                        logger.debug(user_data_load)
                        user_game_list = []
                        user_address_list = []
                        for user_game in user_data_load['game_list']:
                            user_game_list.append(GameInfo(user_game))
                        user_data_load['game_list'] = user_game_list
                        for user_address in user_data_load['address_list']:
                            user_address_list.append(AddressInfo(user_address))
                        user_data_load['address_list'] = user_address_list
                        user_data_dict[user_data_load['mys_uid']] = UserInfo(user_data_load)
                    except (json.decoder.JSONDecodeError, KeyError) as err:
                        logger.warning(f"用户数据{user_data_file}解析失败, 跳过, ")
                        logger_file.warning(f"错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
                        continue
        logger.debug(user_data_dict)
        return user_data_dict
    except KeyboardInterrupt:
        logger.warning("用户强制退出")
        input("按回车键继续")
        sys.exit()
    except Exception as err:
        logger.error(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        input("按回车键继续")
        sys.exit()


user_global_var = GlobalVar()
user_log_control = 'info_all_logger'
logger_file = Logger('only_file_logger').logger
if not user_global_var.init_config.getboolean('log_setting', 'out_file'):
    if user_global_var.init_config.getboolean('log_setting', 'debug'):
        user_log_control = 'debug_console_logger'
    else:
        user_log_control = 'info_console_logger'
    logger_file.disabled = True
else:
    if user_global_var.init_config.getboolean('log_setting', 'debug'):
        user_log_control = 'debug_all_logger'
    else:
        user_log_control = 'info_all_logger'
logger = Logger(user_log_control).logger
user_global_var.clear_type = check_plat()
user_global_var.user_dict = load_user_data()
scheduler = AsyncIOScheduler({'apscheduler.timezone': 'Asia/Shanghai'})
scheduler.add_listener(scheduler_log_listener,
                       EVENT_JOB_ADDED | EVENT_JOB_REMOVED | EVENT_JOB_MODIFIED | EVENT_JOB_MISSED | EVENT_JOB_EXECUTED)

from .exchange_goods import init_exchange, wait_tasks
from .com_tool import async_input, check_update
from .get_info import info_menu
from .mi_tool import check_cookie, update_cookie
