import logging
from typing import Type, Dict, Any, List, Optional, TypeVar

from mongoengine import Document, connect

from eagle_eye_scraper import CONFIG

logger = logging.getLogger()

# 定义一个泛型 T，表示 Document 的子类
T = TypeVar('T', bound=Document)


class MongoHelper:
    """
    通用 MongoDB 操作工具类，整合连接管理和 CRUD 操作。
    """

    def __init__(self, db_name: str):
        """
        初始化 Helper。
        :param db_name: 数据库名称。
        """
        if not CONFIG.ENABLE_MONGODB:
            raise RuntimeError("未启用MONGODB功能！")

        host = CONFIG.MONGODB_HOST
        port = CONFIG.MONGODB_PORT
        username = CONFIG.MONGODB_USER
        password = CONFIG.MONGODB_PASSWORD

        connect(db=db_name, alias=db_name, host=host, port=port, username=username, password=password)

    def create(self, data: T) -> T:
        """
        创建一条记录。
        :param data: Document 子类实例。
        :return: 新创建的文档对象。
        """
        data.save()
        return data

    def read_one(self, model_class: Type[T], query: Dict[str, Any]) -> Optional[T]:
        """
        查询单条记录。
        :param model_class: Document 子类。
        :param query: 查询条件字典。
        :return: 查询到的文档对象，或 None。
        """
        return model_class.objects(**query).first()

    def read_all(self, model_class: Type[T], query: Dict[str, Any] = None) -> List[T]:
        """
        查询多条记录。
        :param model_class: Document 子类。
        :param query: 查询条件字典，可选。
        :return: 文档对象列表。
        """
        query = query or {}
        return list(model_class.objects(**query))

    def update(self, model_class: Type[T], query: Dict[str, Any], update_data: Dict[str, Any]) -> int:
        """
        更新记录。
        :param model_class: Document 子类。
        :param query: 查询条件字典。
        :param update_data: 更新的数据字典。
        :return: 更新的文档数。
        """
        return model_class.objects(**query).update(**update_data)

    def delete(self, model_class: Type[T], query: Dict[str, Any]) -> int:
        """
        删除记录。
        :param model_class: Document 子类。
        :param query: 查询条件字典。
        :return: 删除的文档数。
        """
        return model_class.objects(**query).delete()
