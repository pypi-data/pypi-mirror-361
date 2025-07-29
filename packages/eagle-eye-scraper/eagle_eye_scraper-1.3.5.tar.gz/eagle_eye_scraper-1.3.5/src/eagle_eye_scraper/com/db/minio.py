# -*- coding: utf-8 -*-
import logging

from minio import Minio

from eagle_eye_scraper import CONFIG

__all__ = ['minio_client']

logger = logging.getLogger()

if CONFIG.ENABLE_MINIO:
    minio_client = Minio(CONFIG.MINIO_ENDPOINT,
                         access_key=CONFIG.MINIO_ACCESS_KEY,
                         secret_key=CONFIG.MINIO_SECRET_KEY,
                         secure=CONFIG.MINIO_SECURE)
else:
    logger.warn("未启用Minio")
    minio_client = None
