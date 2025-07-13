import redis
import hashlib
import json
import os

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

rdb = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

def cache_key_for_prompt(prompt: str) -> str:
    h = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    return f"rag:response:{h}"

def get_cached_response(prompt: str) -> str | None:
    key = cache_key_for_prompt(prompt)
    return rdb.get(key)

def set_cached_response(prompt: str, response: str, ttl=3600):
    key = cache_key_for_prompt(prompt)
    rdb.set(key, response, ex=ttl)
