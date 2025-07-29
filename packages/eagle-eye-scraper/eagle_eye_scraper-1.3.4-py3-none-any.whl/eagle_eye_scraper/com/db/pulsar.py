import logging

import pulsar

from eagle_eye_scraper import CONFIG

__all__ = ['pulsar_client']

logger = logging.getLogger()

if CONFIG.ENABLE_PULSAR:
    pulsar_client = pulsar.Client(CONFIG.PULSAR_URL)
else:
    pulsar_client = None
