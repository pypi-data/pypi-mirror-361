from typing import List

from pydantic import BaseModel, Field


class SpiderDispatcher(BaseModel):
    cron_exp: str
    spider_class: str
    func_call: str
    func_kwargs: dict = Field(default={})


class SpiderGroup(BaseModel):
    group_name: str
    dispatchers: List[SpiderDispatcher]
