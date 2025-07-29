import json
import logging
import multiprocessing
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from pathlib import Path

import yaml
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from eagle_eye_scraper import CONFIG
from eagle_eye_scraper.com.constant.mq_constant import SPIDER_DISPATCH_QUEUE
from eagle_eye_scraper.com.db.pulsar import pulsar_client
from eagle_eye_scraper.com.domains import SpiderGroup
from eagle_eye_scraper.com.mq.pullsar.messages import DispatchTaskPulsarMessage
from eagle_eye_scraper.com.utils.time_util import TimeUtils

logger = logging.getLogger()


class SpiderDispatchProducer:
    producer_name = CONFIG.PROJECT_NAME + '-spider-dispatch-producer'

    def __init__(self, pulsar_client, job_dir="resources"):
        self.producer = pulsar_client.create_producer(topic=SPIDER_DISPATCH_QUEUE, producer_name=self.producer_name)
        self.scheduler = BackgroundScheduler()
        self.job_dir = job_dir

    def produce_dispatch(self, spider_class, func_call, **func_kwargs):
        try:
            message = DispatchTaskPulsarMessage(spider_class=spider_class, func_call=func_call, func_kwargs=func_kwargs)
            content = json.dumps(asdict(message)).encode('utf-8')
            self.producer.send(content)
        except Exception as e:
            logger.error(f"推送spider任务分布式调度出错：{e}")

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
        logger.info("启用spider分布式调度器")

    def stop(self):
        self.scheduler.shutdown()
        logger.info("停止spider分布式调度器")


class SpiderDispatchPoolExecutor:

    def __init__(self, max_workers=4):
        self.max_workers = max_workers
        self._running = multiprocessing.Value('b', False)  # 跨进程共享标志
        self._process_pool = []
        self._monitor_thread = None

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

    def _worker_process(self, msg: str):
        """在工作进程中处理单条消息。"""
        try:
            item = DispatchTaskPulsarMessage(json.loads(msg))
            Spider = self._resolve(item.spider_class)
            instance = Spider()
            getattr(instance, item.func_call)(kwargs=item.func_kwargs)
        except Exception as e:
            logger.error(f"[Worker Error] 消息处理失败：{e}")

    def _consume(self, running_flag, process_id):
        logger.info(f"启动消费者进程 {process_id}")
        consumer = pulsar_client.subscribe(topic=SPIDER_DISPATCH_QUEUE)
        while running_flag.value:
            try:
                msg = consumer.receive(timeout_millis=10000)
                if msg:
                    logger.info("Received message '{0}' id='{1}'".format(msg.data().decode('utf-8'), msg.message_id()))
                    self._worker_process(msg.data().decode('utf-8'))
                    consumer.acknowledge(msg)
            except Exception as e:
                logger.error(f"[Consume Error] 消息消费失败：{e}", exc_info=True)

    def _start_consumer(self, process_id):
        """启动单个消费者进程"""
        process = multiprocessing.Process(
            target=self._consume,
            args=(self._running, process_id),
            name=f"Consumer-{process_id}"
        )
        process.start()
        return process

    def _monitor_processes(self):
        """监控进程池中的消费者进程，自动补全异常退出的进程"""
        logger.info("启动进程监控线程")
        while self._running.value:
            for i, process in enumerate(self._process_pool):
                if not process.is_alive():
                    logger.warning(f"消费者进程 {process.name} 已退出，正在重启...")
                    new_process = self._start_consumer(i)
                    self._process_pool[i] = new_process
            time.sleep(5)  # 每 5 秒检查一次进程状态
        logger.info("监控线程已停止")

    def start(self):
        """启动 SpiderDispatchExecutor 服务。"""
        if self._running.value:
            logger.warning("服务已在运行中")
            return

        logger.info("启动 SpiderDispatchExecutor...")
        self._running.value = True
        # 启动消费者进程池
        self._process_pool = [
            self._start_consumer(i) for i in range(self.max_workers)
        ]

        self._monitor_thread = threading.Thread(target=self._monitor_processes, daemon=True)
        self._monitor_thread.start()

    def stop(self):
        """停止 SpiderDispatchExecutor 服务。"""
        if not self._running.value:
            logger.warning("服务未运行")
            return

        logger.info("停止 SpiderDispatchExecutor...")
        self._running.value = False

        # 终止所有子进程
        for process in self._process_pool:
            process.terminate()
            process.join()
        self._process_pool = []

        # 等待后台线程结束
        if self._monitor_thread:
            self._monitor_thread.join()
            self._monitor_thread = None

    def _handle_signal(self, signum, frame):
        """信号处理器，用于捕获终止信号。"""
        logger.info(f"收到信号 {signum}，停止服务...")
        self.stop()
