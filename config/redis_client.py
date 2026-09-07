import redis
from config.settings import REDIS_URL, REDIS_HOST, REDIS_PORT, REDIS_DB


def get_redis_connection():
    if REDIS_URL:
        # Cloud Redis providers (Upstash, Redis Cloud, ...) hand out a single
        # connection URL - use it as-is when present.
        return redis.from_url(REDIS_URL)
    return redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
