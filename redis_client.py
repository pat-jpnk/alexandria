import redis

try:
    redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)
except redis.exceptions.RedisError as e:
    # TODO: log error e
