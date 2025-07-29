import logging

from eagle_eye_scraper.com.mq.ram.ram_mq import RamMQClient
from eagle_eye_scraper.dispatch.host_dispatcher import HostDispatchProducer
from eagle_eye_scraper.dispatch.ram_dispatcher import SpiderDispatchProducer, SpiderDispatchExecutor
from eagle_eye_scraper.scheduler_visual import start_visual_scheduler

logger = logging.getLogger()


def enable_ram_dispatch():
    try:
        mq_client = RamMQClient()

        executor = SpiderDispatchExecutor(mq_client=mq_client)
        executor.start()

        producer = SpiderDispatchProducer(mq_client=mq_client)
        producer.start()
    except Exception as e:
        logger.error(e, exc_info=True)


def enable_host_dispatch():
    try:
        start_visual_scheduler()
        dispatcher = HostDispatchProducer()
        dispatcher.start()
    except Exception:
        logger.error("启动单主机调度失败", exc_info=True)
