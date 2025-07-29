import logging
from pymongo import MongoClient

from eagle_eye_scraper import CONFIG

__all__ = ['mongo_client']

logger = logging.getLogger()

if CONFIG.ENABLE_MONGODB:
    mongo_client = MongoClient(
        host=CONFIG.MONGODB_HOST,
        port=CONFIG.MONGODB_PORT,
        username=CONFIG.MONGODB_USER,
        password=CONFIG.MONGODB_PASSWORD,
        authSource='admin',
        maxPoolSize=32,
    )
else:
    logger.warn("未启用Mongodb")
    mongo_client = None
