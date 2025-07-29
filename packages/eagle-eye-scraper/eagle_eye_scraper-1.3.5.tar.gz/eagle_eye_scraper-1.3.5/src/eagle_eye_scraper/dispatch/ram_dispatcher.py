import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from multiprocessing import Semaphore
from pathlib import Path
from queue import Empty

import yaml
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from eagle_eye_scraper.com.domains import SpiderGroup
from eagle_eye_scraper.com.mq.ram import DispatchTaskMessage
from eagle_eye_scraper.com.utils.time_util import TimeUtils

logger = logging.getLogger()


class SpiderDispatchProducer:
    def __init__(self, mq_client, job_dir="resources"):
        self.mq_client = mq_client
        self.scheduler = BackgroundScheduler()
        self.job_dir = job_dir

    def produce_dispatch(self, spider_class, func_call, **func_kwargs):
        try:
            message = DispatchTaskMessage(spider_class=spider_class, func_call=func_call, func_kwargs=func_kwargs)
            self.mq_client.push_message(message)
        except Exception as e:
            logger.error(f"推送spider任务调度出错：{e}")

    def load_spider_group(self, job_file):
        try:
            with open(job_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                return SpiderGroup(**data)
        except Exception as e:
            logger.error(f"加载spider配置出错:{job_file}", exc_info=True)
        return None

    def load_spider_job(self):
        default_dir = Path(self.job_dir)
        if not default_dir.exists():
            raise FileNotFoundError(f"文件目录不存在: {self.job_dir}")
        job_files = [file for file in default_dir.rglob('*.yml') if file.is_file()]

        for job_file in job_files:
            spider_group = self.load_spider_group(job_file)
            if not spider_group:
                continue
            for dispatcher in spider_group.dispatchers:
                trigger = CronTrigger.from_crontab(dispatcher.cron_exp, timezone=TimeUtils.shanghai_tz)
                self.scheduler.add_job(trigger=trigger, func=self.produce_dispatch,
                                       args=(dispatcher.spider_class, dispatcher.func_call,),
                                       kwargs=dispatcher.func_kwargs)

    def start(self):
        jobstores = {"default": MemoryJobStore()}
        executors = {"default": ThreadPoolExecutor(20)}
        job_defaults = {
            'misfire_grace_time': 30,  # 任务最多允许延迟 30 秒
            'coalesce': True,  # 合并错过的任务为一次运行
            'max_instances': 2  # 每个任务最多允许运行 2 个实例
        }
        self.scheduler.configure(jobstores=jobstores, executors=executors,
                                 job_defaults=job_defaults, timezone=TimeUtils.shanghai_tz)
        self.load_spider_job()
        self.scheduler.start()
        logger.info("启用spider内存型调度器")

    def stop(self):
        self.scheduler.shutdown()
        logger.info("停止spider调度器")


class SpiderDispatchExecutor:
    def __init__(self, mq_client, max_workers=4):
        self.mq_client = mq_client
        self.max_workers = max_workers
        self._running = False
        self._worker_pool = None
        self._semaphore = Semaphore(max_workers)
        self._thread = None

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

    def _task_done(self, future, message):
        self.mq_client.send_ack(message)
        self._semaphore.release()

    def _worker_process(self, message):
        """在工作进程中处理单条消息。"""
        try:
            Spider = self._resolve(message.spider_class)
            instance = Spider()
            getattr(instance, message.func_call)(kwargs=message.func_kwargs)
        except Exception as e:
            logger.error(f"[Worker Error] 消息处理失败：{e}")

    def _blocking_submit(self, message):
        """提交任务到进程池，当无空闲进程时阻塞等待。"""
        self._semaphore.acquire()
        future = self._worker_pool.submit(self._worker_process, message)
        future.add_done_callback(partial(self._task_done, message=message))
        return future

    def _dispatch_tasks(self):
        """主循环，从队列中获取任务并提交到进程池。"""
        while self._running:
            try:
                message = self.mq_client.get_message(timeout=10)  # 从队列中获取任务
                if not message:
                    continue

                self._blocking_submit(message)  # 提交任务到进程池
            except Empty:
                logger.debug("Queue is empty.")
                continue  # 队列为空，继续循环
            except Exception as e:
                logger.error(f"[Dispatch Error] 任务调度失败：{e}", exc_info=True)

    def start(self):
        """启动 SpiderDispatchExecutor 服务。"""
        if self._running:
            logger.warning("服务已在运行中")
            return

        logger.info("启动 SpiderDispatchExecutor...")
        self._running = True

        # 初始化进程池
        self._worker_pool = ThreadPoolExecutor(max_workers=self.max_workers)

        # 启动调度线程
        self._thread = threading.Thread(target=self._dispatch_tasks, daemon=True)
        self._thread.start()

    def stop(self):
        """停止 SpiderDispatchExecutor 服务。"""
        if not self._running:
            logger.warning("服务未运行")
            return

        logger.info("停止 SpiderDispatchExecutor...")
        self._running = False

        # 等待调度线程结束
        if self._thread:
            self._thread.join()

        # 关闭进程池
        if self._worker_pool:
            self._worker_pool.shutdown(wait=True)
