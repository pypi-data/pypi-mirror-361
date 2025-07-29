import logging

from redis import Redis
from rediscluster import ClusterConnectionPool, RedisCluster

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
        nodes = []
        for item in CONFIG.REDIS_HOST.split(','):
            host, port = item.split(':')
            node = {"host": host, "port": port}
            nodes.append(node)
        pool = ClusterConnectionPool(
            startup_nodes=nodes,
            password=CONFIG.REDIS_PASSWORD,
            decode_responses=True,
            max_connections=16,
            socket_timeout=15
        )
        redis_client = RedisCluster(connection_pool=pool)
else:
    logger.warn("未启用redis")
    redis_client = None
