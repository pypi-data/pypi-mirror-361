import logging

from eagle_eye_scraper.com.constant.mq_constant import SPIDER_DISPATCH_QUEUE
from eagle_eye_scraper.com.mq.ram import BoundedPriorityQueue
from eagle_eye_scraper.com.mq.ram.messages import PriorityMessage

logger = logging.getLogger()


class RamMQClient:
    queue = None

    def __init__(self):
        self.queue = BoundedPriorityQueue(SPIDER_DISPATCH_QUEUE, 500)

    def push_message(self, message: PriorityMessage):
        self.queue.put(message)

    def get_message(self, timeout=10):
        return self.queue.get(timeout)

    def send_ack(self, message: PriorityMessage):
        self.queue.complete(message)
