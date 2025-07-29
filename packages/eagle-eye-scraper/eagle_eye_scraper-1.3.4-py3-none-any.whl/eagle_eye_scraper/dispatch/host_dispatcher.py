import logging
import socket
import time
from pathlib import Path
from urllib.parse import urlparse

import requests
import yaml
from pytz import timezone

from eagle_eye_scraper.com.domains import SpiderGroup

logger = logging.getLogger()

shanghai_tz = timezone('Asia/Shanghai')


SCHEDULER_HOST = "127.0.0.1"
SCHEDULER_PORT = 9000


class HostDispatchProducer:

    def __init__(self, job_dir="resources"):
        self.job_dir = job_dir

    def _wait_for_http(self, timeout: int = 60):
        """等待主机端口可用"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(10)  # 设置单次连接超时时间
                if sock.connect_ex((SCHEDULER_HOST, SCHEDULER_PORT)) == 0:  # 0 表示端口开放
                    logger.info(f"{SCHEDULER_HOST}:{SCHEDULER_PORT} 可用，继续执行代码")
                    return True
            logger.info(f"尝试连接 {SCHEDULER_HOST}:{SCHEDULER_PORT} 失败，等待重试...")
            time.sleep(1)  # 每秒尝试一次

        logger.info(f"超时 {timeout} 秒，{SCHEDULER_HOST}:{SCHEDULER_PORT} 仍不可用")
        return False

    def _register_spider_job(self, cron_exp, spider, func, **kwargs):
        #  注册spider调度任务
        try:
            url = "http://127.0.0.1:9000/job/new/spider"
            headers = {
                "accept": "application/json",
                "Content-Type": "application/json"
            }
            data = {
                "crom_expr": cron_exp,
                "spider_class": spider,
                "spider_func": func,
                "func_kwargs": kwargs
            }
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            resp_data = response.json()
            register_success = resp_data['success']
            logger.info(f"注册调度器 {spider}::{func} {register_success}")
        except Exception:
            logger.error("注册spider-job报错", exc_info=True)

    def _load_spider_group(self, job_file):
        try:
            with open(job_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                return SpiderGroup(**data)
        except Exception as e:
            logger.error(f"加载spider配置出错:{job_file}", exc_info=True)
        return None

    def load_spider_dispatcher(self):
        default_dir = Path(self.job_dir)
        if not default_dir.exists():
            raise FileNotFoundError(f"文件目录不存在: {self.job_dir}")
        job_files = [file for file in default_dir.rglob('*.yml') if file.is_file()]

        for job_file in job_files:
            spider_group = self._load_spider_group(job_file)
            if not spider_group:
                continue

            if self._wait_for_http():
                time.sleep(3)
                for d in spider_group.dispatchers:
                    self._register_spider_job(d.cron_exp, d.spider_class, d.func_call, **d.func_kwargs)

    def start(self):
        self.load_spider_dispatcher()


class HostDispatchExecutor:

    def _resolve(self, name):
        """解析一个点分字符串（模块名.类名），并返回对应的全局对象。"""
        name = name.split('.')
        used = name.pop(0)
        found = __import__(used)
        for n in name:
            used = used + '.' + n
            try:
                found = getattr(found, n)
            except AttributeError:
                __import__(used)
                found = getattr(found, n)
        return found

    def call_executor(self, spider_class, func_call, **func_kwargs):
        try:
            Spider = self._resolve(spider_class)
            instance = Spider()
            getattr(instance, func_call)(kwargs=func_kwargs)
        except Exception as e:
            logger.error(f"spider执行失败：{e}")
