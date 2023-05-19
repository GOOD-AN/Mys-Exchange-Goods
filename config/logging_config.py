"""
日志配置
"""
log_config = {
    "version": 1,
    "formatters": {
        "simplify_output": {
            "format": "%(message)s"
        },
        "full_output": {
            "format": "[%(asctime)s] MEG.%(levelname)s: (%(module)s) >>> %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S %z"
        }
    },
    "filters": {},
    "handlers": {
        "standard_console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "simplify_output"
        },
        "standard_file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "level": "DEBUG",
            "formatter": "full_output",
            "filename": "log/default_log.log",
            "when": 'D',
            "interval": 1,
            "backupCount": 5,
            "encoding": "utf-8"
        },
        "debug_console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "full_output"
        }
    },
    "loggers": {
        "info_all_logger": {
            "handlers": ["standard_console", "standard_file"],
            "level": "INFO",
            "propagate": False
        },
        "debug_all_logger": {
            "handlers": ["debug_console", "standard_file"],
            "level": "DEBUG",
            "propagate": False
        },
        "info_console_logger": {
            "handlers": ["standard_console"],
            "level": "INFO",
            "propagate": False
        },
        "debug_console_logger": {
            "handlers": ["debug_console"],
            "level": "DEBUG",
            "propagate": False
        },
        "only_file_logger": {
            "handlers": ["standard_file"],
            "level": "INFO",
            "propagate": False
        },
        "only_debug_file_logger": {
            "handlers": ["standard_file"],
            "level": "DEBUG",
            "propagate": False
        }
    },
    "root": {},
    "incremental": False,
    "disable_existing_loggers": False
}
