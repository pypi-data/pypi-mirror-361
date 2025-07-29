import logging

from redis import Redis
from redis.cluster import ClusterNode, RedisCluster

from eagle_eye_scraper import CONFIG

__all__ = ['redis_client']

logger = logging.getLogger()

if CONFIG.ENABLE_REDIS:
    if CONFIG.ENABLE_REDIS:
        if CONFIG.REDIS_TYPE == 'alone':
            redis_client = Redis(
                CONFIG.REDIS_HOST,
                CONFIG.REDIS_PORT,
                CONFIG.REDIS_DATABASE,
                CONFIG.REDIS_PASSWORD,
                decode_responses=True,
            )
    elif CONFIG.REDIS_TYPE == 'cluster':
        nodes = [ClusterNode(host=host, port=CONFIG.REDIS_PORT) for host in CONFIG.REDIS_HOST.split(',')]
        redis_client = RedisCluster(
            startup_nodes=nodes,
            password=CONFIG.REDIS_PASSWORD,
            decode_responses=True,
            max_connections=CONFIG.REDIS_MAX_CONNECTIONS,
            socket_timeout=30,
            socket_connect_timeout=30,
            skip_full_coverage_check=True,
            health_check_interval=30
        )

else:
    logger.warn("未启用redis")
    redis_client = None
