from dataclasses import dataclass, field
from datetime import datetime
from itertools import count

from pydantic import BaseModel, Field

from eagle_eye_scraper.com.utils.time_util import TimeUtils

msg_id_generator = count(1)


class SpiderDispatchMessage(BaseModel):
    task_name: str = Field()
    spider_name: str = Field()
    spider_call: str = Field()
    dispatch_time: datetime = Field(default_factory=datetime.now)


@dataclass
class BaseMessage:
    mid: int = field(default_factory=lambda: next(msg_id_generator), compare=False)
    pub_time: datetime = field(default_factory=TimeUtils.get_now_time, compare=False)


@dataclass
class DispatchTaskPulsarMessage(BaseMessage):
    spider_class: str = field(default=None)
    func_call: str = field(default=None)
    func_kwargs: dict = field(default=None)
