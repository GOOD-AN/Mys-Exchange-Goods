"""
日志配置
"""
log_config = {
    "version": 1.0,
    "formatters": {
        "standard_out": {
            "format": "%(message)s"
        },
        "standard_file": {
            "format": "[%(asctime)s] MEG.%(levelname)s: (%(module)s) >>> %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S %z"
        }
    },
    "filters": {},
    "handlers": {
        "standard_console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "standard_out"
        },
        "standard_file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "level": "INFO",
            "formatter": "standard_file",
            "filename": "log/default_log.log",
            "when": 'D',
            "interval": 1,
            "backupCount": 5,
            "encoding": "utf-8"
        }
    },
    "loggers": {
        "standard_logger": {
            "handlers": ["standard_console", "standard_file"],
            "level": "INFO",
            "propagate": False
        },
        "debug_logger": {
            "handlers": ["standard_console"],
            "level": "DEBUG",
            "propagate": False
        }
    },
    "root": {},
    "incremental": False,
    "disable_existing_loggers": False
}
