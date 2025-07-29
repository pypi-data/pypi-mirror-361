from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum
from itertools import count

msg_id_generator = count(1)


class Status(IntEnum):
    PENDING = 0
    PROCESSING = 1
    COMPLETED = 2


@dataclass(order=True)
class PriorityMessage(ABC):
    mid: int = field(default_factory=lambda: next(msg_id_generator), compare=False)
    create_time: datetime = field(default_factory=datetime.now, compare=False)
    priority: int = field(default=5)
    status: str = field(default=Status.PENDING, compare=False)


@dataclass(order=True)
class DispatchTaskMessage(PriorityMessage):
    spider_class: str = field(default=None)
    func_call: str = field(default=None)
    func_kwargs: dict = field(default=None)
