import logging
from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from eagle_eye_scraper import CONFIG

__all__ = ['SessionLocal', 'Model', 'mysql_engine']

Base = declarative_base()

logger = logging.getLogger()

if CONFIG.ENABLE_MYSQL:
    db_url = f"mysql+pymysql://{CONFIG.MYSQL_USER}:{CONFIG.MYSQL_PASSWORD}@{CONFIG.MYSQL_HOST}:{CONFIG.MYSQL_PORT}/{CONFIG.MYSQL_DEFAULT_DATABASE}"
    mysql_engine = create_engine(db_url, pool_recycle=3600, echo=False)
    SessionLocal = sessionmaker(autocommit=True, autoflush=True, bind=mysql_engine)
else:
    logger.warn("未启用mysql")
    SessionLocal = None


class Model:

    def __init__(self):
        if not CONFIG.ENABLE_MYSQL:
            raise RuntimeError("未启用MYSQL功能！")

    id = Column(Integer, primary_key=True)
    created_time = Column(DateTime, default=datetime.now())
    updated_time = Column(DateTime, default=datetime.now(), onupdate=datetime.now())
