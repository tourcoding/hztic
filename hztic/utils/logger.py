import logging
import os
from logging.config import dictConfig
from hztic.config import LOG_DIR
import inspect

class Logger:
    _configured = False
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Logger, cls).__new__(cls)
        return cls._instance

    def __init__(self, name=None, log_dir=LOG_DIR, log_file="app.log", level=logging.DEBUG, max_bytes=10 * 1024 * 1024, backup_count=3):
        """
        初始化日志配置
        :param name: 日志名称（可选，默认使用调用者的模块名）
        :param log_dir: 日志目录
        :param log_file: 日志文件名
        :param level: 日志级别
        :param max_bytes: 日志文件最大大小（字节）
        :param backup_count: 备份文件数量
        """
        
        # 如果没有指定 name，则使用调用者的模块名
        if name is None:
            frame = inspect.stack()[1]
            module = inspect.getmodule(frame[0])
            self.name = module.__name__ if module else "unknown"
        else:
            self.name = name

        self.log_dir = log_dir
        self.log_file = log_file
        self.level = level
        self.max_bytes = max_bytes
        self.backup_count = backup_count

        # 创建日志目录
        os.makedirs(self.log_dir, exist_ok=True)

        # 配置日志
        if not Logger._configured:
            self._configure_logger()
            Logger._configured = True

    def _configure_logger(self):
        """配置日志"""
        # 日志配置字典
        logging_config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    # 修改日志格式
                    "format": "[%(asctime)s] [%(levelname)s] [%(name)s] [%(filename)s:%(lineno)d] - %(message)s",
                },
            },
            "handlers": {
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "filename": os.path.join(self.log_dir, self.log_file),
                    "maxBytes": self.max_bytes,
                    "backupCount": self.backup_count,
                    "encoding": "utf-8",
                    "formatter": "default",
                },
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                },
            },
            "loggers": {
                self.name: {
                    "level": self.level,
                    "handlers": ["file", "console"],
                    "propagate": False,  # 禁止向上传播
                },
            },
            "root": {  # 配置根日志记录器
                "level": self.level,
                "handlers": ["file", "console"],
            },
        }

        # 应用日志配置
        dictConfig(logging_config)

    def get_logger(self):
        """获取日志对象"""
        return logging.getLogger(self.name)