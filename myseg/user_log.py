"""
日志
"""
import logging.config

from config import logging_config
from myseg.global_var import user_global_var as gl


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


user_log_control = 'info_all_logger'
logger_file = Logger('only_file_logger').logger
if not gl.init_config.getboolean('log_setting', 'out_file'):
    if gl.init_config.getboolean('log_setting', 'debug'):
        user_log_control = 'debug_console_logger'
    else:
        user_log_control = 'info_console_logger'
    logger_file.disabled = True
else:
    if gl.init_config.getboolean('log_setting', 'debug'):
        user_log_control = 'debug_all_logger'
    else:
        user_log_control = 'info_all_logger'
logger = Logger(user_log_control).logger
