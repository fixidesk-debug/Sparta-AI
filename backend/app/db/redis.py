import redis
from app.core.config import settings

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

def get_redis():
    return redis_client

def cache_set(key: str, value: str, expire: int = 3600):
    """Set a cache value with expiration time in seconds"""
    redis_client.setex(key, expire, value)

def cache_get(key: str):
    """Get a cache value"""
    return redis_client.get(key)

def cache_delete(key: str):
    """Delete a cache value"""
    redis_client.delete(key)
