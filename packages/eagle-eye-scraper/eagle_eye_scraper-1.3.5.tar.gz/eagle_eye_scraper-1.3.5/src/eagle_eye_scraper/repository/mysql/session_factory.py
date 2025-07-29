import functools
import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from eagle_eye_scraper import CONFIG

logger = logging.getLogger()

if CONFIG.ENABLE_MYSQL:
    host = CONFIG.MYSQL_HOST
    port = CONFIG.MYSQL_PORT
    db_name = CONFIG.MYSQL_DEFAULT_DATABASE
    username = CONFIG.MYSQL_USER
    password = CONFIG.MYSQL_PASSWORD
    db_url = f"mysql+pymysql://{username}:{password}@{host}:{port}/{db_name}"
    engine = create_engine(db_url, pool_recycle=3600, echo=False)
    SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)
else:
    engine = None
    SessionLocal = None


def connect(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not CONFIG.ENABLE_MYSQL:
            logger.warning("未启用MYSQL功能，跳过数据库操作！")
            return func(*args, **kwargs)

        session = kwargs.get('session', None)
        if session is None:
            logger.debug('new mysql session connect')
            session = SessionLocal()
        try:
            kwargs.setdefault('session', session)
            return func(*args, **kwargs)
        except Exception as e:
            logger.exception(e, exc_info=True)
        finally:
            session.close()

    return wrapper
