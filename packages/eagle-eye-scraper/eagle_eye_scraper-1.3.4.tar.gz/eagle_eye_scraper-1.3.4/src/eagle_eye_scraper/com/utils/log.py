# -*- coding: utf-8 -*-
import json
import logging
import os
import platform
from logging import LogRecord
from logging.config import dictConfig
from typing import Optional, Tuple

from concurrent_log_handler import ConcurrentRotatingFileHandler

PROJECT_NAME = os.environ.get("PROJECT_NAME", "eagle-eye-scraper")
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
LOG_PATH = os.environ.get("LOG_PATH", "/data/logs")


class FileFormatter(logging.Formatter):

    def format(self, record: LogRecord):
        record.hostname = f'{platform.node()}'

        # 判定 msg 是否为字典、列表、集合等可序列化的类型
        if isinstance(record.msg, (dict, list, set)):
            try:
                # 将 msg 转换为 JSON 字符串
                record.msg = json.dumps(record.msg, ensure_ascii=False)
            except TypeError:
                # 如果序列化失败，输出原始的非序列化内容
                record.msg = str(record.msg)
        return super().format(record)


class MyRotatingFileHandler(ConcurrentRotatingFileHandler):

    def __init__(self, filename: str, mode: str = "a", maxBytes: int = 0, backupCount: int = 0,
                 encoding: Optional[str] = None, debug: bool = False, delay: None = None,
                 use_gzip: bool = False, owner: Optional[Tuple[str, str]] = None, chmod: Optional[int] = None,
                 umask: Optional[int] = None, newline: Optional[str] = None,
                 terminator: str = "\n", unicode_error_policy: str = "ignore",
                 lock_file_directory: Optional[str] = None):
        super().__init__(filename, mode, maxBytes, backupCount, encoding, debug, delay, use_gzip, owner, chmod, umask,
                         newline, terminator, unicode_error_policy,
                         lock_file_directory)


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
    },
    'formatters': {
        'console-fmt': {
            'format': '%(asctime)s [%(levelname)s] | %(message)s'
        },
        'file-fmt': {
            '()': FileFormatter,
            'format': '%(asctime)s | %(hostname)s %(process)d [%(levelname)s] [%(funcName)s] |  %(message)s'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'console-fmt'
        },
        'file': {
            'class': 'eagle_eye_scraper.com.utils.log.MyRotatingFileHandler',
            'filename': f'{LOG_PATH}/{PROJECT_NAME}.log',
            'mode': 'a',
            'backupCount': 5,
            'maxBytes': 524288000,
            'encoding': 'utf8',
            'use_gzip': True,
            'formatter': 'file-fmt'
        },
    },
    'loggers': {
        '': {
            'handlers': ['console', 'file'],
            'level': LOG_LEVEL,
        },
    },
}


def enable_logger():
    dictConfig(LOGGING)
