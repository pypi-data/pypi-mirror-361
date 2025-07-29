import logging
from abc import abstractmethod

logger = logging.getLogger()


class Spider:

    def up_report(self, status: int):
        pass

    def terminate(self):
        pass

    def start(self):
        logger.info("spider starting!")
        self.up_report(1)

    def finish(self):
        logger.info("spider finished!")
        self.up_report(-1)
        self.terminate()

    def send_fetch_msg(self, cls_name, data):
        pass

    def receive_fetch_msg(self):
        pass

    @abstractmethod
    def crawl(self, **kwargs):
        pass

    @abstractmethod
    def parse(self, **kwargs):
        pass
