import logging
from typing import Type, TypeVar, Dict, Any, List, Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base

from eagle_eye_scraper import CONFIG
from eagle_eye_scraper.repository.mysql.session_factory import connect

logger = logging.getLogger()

# SQLAlchemy 基础类
Base = declarative_base()

# 定义泛型
T = TypeVar('T', bound=Base)


class MySQLHelper:
    """
    通用 MySQL 辅助工具类，基于 SQLAlchemy 实现。
    """

    def __init__(self):
        if not CONFIG.ENABLE_MYSQL:
            raise RuntimeError("未启用MYSQL功能！")

    @connect
    def create(self, model: T, **kwargs) -> T:
        """
        创建一条记录。
        :param model: SQLAlchemy 模型类，Base 的子类。
        :param data: 数据字典。
        :return: 新创建的记录对象。
        """
        session = kwargs.get('session')
        try:
            instance = model
            session.add(instance)
            session.commit()
            return instance
        except SQLAlchemyError:
            session.rollback()
            logger.error("❌ Failed to create record:", exc_info=True)

    @connect
    def read_one(self, model: Type[T], query: Dict[str, Any], **kwargs) -> Optional[T]:
        """
        查询单条记录。
        :param model: SQLAlchemy 模型类，Base 的子类。
        :param query: 查询条件字典。
        :return: 查询到的记录对象，或 None。
        """
        session = kwargs.get('session')
        try:
            return session.query(model).filter_by(**query).first()
        except SQLAlchemyError:
            logger.error("❌ Failed to read record:", exc_info=True)

    @connect
    def read_all(self, model: Type[T], query: Dict[str, Any], **kwargs) -> List[T]:
        """
        查询多条记录。
        :param model: SQLAlchemy 模型类，Base 的子类。
        :param query: 查询条件字典，可选。
        :return: 记录对象列表。
        """
        session = kwargs.get('session')
        try:
            return session.query(model).filter_by(**query).all()
        except SQLAlchemyError as e:
            logger.error("❌ Failed to read records:", exc_info=True)
            raise

    @connect
    def update(self, model: Type[T], query: Dict[str, Any], update_data: Dict[str, Any], **kwargs) -> int:
        """
        更新记录。
        :param model: SQLAlchemy 模型类，Base 的子类。
        :param query: 查询条件字典。
        :param update_data: 更新数据字典。
        :return: 更新的记录数。
        """
        session = kwargs.get('session')
        try:
            records = session.query(model).filter_by(**query)
            updated_count = records.update(update_data)
            session.commit()
            return updated_count
        except SQLAlchemyError as e:
            session.rollback()
            logger.error("❌ Failed to update records:", exc_info=True)
            raise

    @connect
    def delete(self, model: Type[T], query: Dict[str, Any], **kwargs) -> int:
        """
        删除记录。
        :param model: SQLAlchemy 模型类，Base 的子类。
        :param query: 查询条件字典。
        :return: 删除的记录数。
        """
        session = kwargs.get('session')
        try:
            records = session.query(model).filter_by(**query)
            deleted_count = records.delete()
            session.commit()
            return deleted_count
        except SQLAlchemyError as e:
            session.rollback()
            logger.error("❌ Failed to delete records:", exc_info=True)
            raise
