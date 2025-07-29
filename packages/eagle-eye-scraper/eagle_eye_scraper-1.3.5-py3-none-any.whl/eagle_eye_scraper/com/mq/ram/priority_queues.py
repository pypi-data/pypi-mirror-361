import logging
import threading
from queue import PriorityQueue, Full

from .messages import PriorityMessage, Status

logger = logging.getLogger()


class BoundedPriorityQueue:
    def __init__(self, queue_name: str, maxsize: int):
        self.queue = PriorityQueue(maxsize)
        self.queue_name = queue_name
        self.lock = threading.Lock()
        self.tracker = {}

    def put(self, message: PriorityMessage):
        with self.lock:
            if message.priority > 10:
                raise ValueError(f"{self.queue} Message priority cannot exceed 10")
            try:
                self.queue.put(message, timeout=1)
                self.tracker[message.mid] = {"status": message.status, "priority": message.priority}
                logger.info(f"Message added: {message}")
            except Full as e:
                logger.error(f"Queue is full. Message rejected. {e}")

    def get(self, timeout=10):
        with self.lock:
            message = self.queue.get(block=True, timeout=timeout)
            self.tracker[message.mid]["status"] = Status.PROCESSING
            logger.debug(f"Message retrieved: {message}")
            return message

    def complete(self, message: PriorityMessage):
        with self.lock:
            self.tracker[message.mid]["status"] = Status.COMPLETED
            self.queue.task_done()
            logger.info(f"Message completed: {message}")
            del self.tracker[message.mid]

    def status(self, mid: int):
        with self.lock:
            return self.tracker.get(mid, None)
