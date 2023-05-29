"""
日志
"""
import sys

import logging.config
from typing import Tuple

from config import logging_config
from .global_var import user_global_var as gl


class Logger:
    """
    日志
    """

    def __init__(self, log_control, user_log_path=None):
        # 自定义日志路径与名称
        log_path = gl.basic_path / 'log' / 'meg_all.log'
        if user_log_path:
            log_path = user_log_path
        if not log_path.parent.exists():
            log_path.parent.mkdir(parents=True, exist_ok=True)
        logging_config.log_config['handlers']['standard_file']['filename'] = log_path
        logging.config.dictConfig(logging_config.log_config)
        self.logger = logging.getLogger(log_control)


def get_logger() -> Tuple[Logger, Logger]:
    """
    获取日志
    """
    try:
        logger_main = Logger('only_file_logger').logger
        if not gl.init_config.getboolean('log_setting', 'out_file'):
            if gl.init_config.getboolean('log_setting', 'debug'):
                user_log_control = 'debug_console_logger'
            else:
                user_log_control = 'info_console_logger'
            logger_main = Logger(user_log_control).logger
        else:
            if gl.init_config.getboolean('log_setting', 'debug'):
                user_log_control = 'debug_all_logger'
                logger_main = Logger("only_debug_file_logger").logger
            else:
                user_log_control = 'info_all_logger'
        logger_one = Logger(user_log_control).logger
        return logger_one, logger_main
    except KeyboardInterrupt:
        print("用户强制退出")
        sys.exit()
    except Exception as err:
        print(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        sys.exit()


logger, logger_file = get_logger()
