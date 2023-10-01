import redis

'''
https://pypi.org/project/redis/

https://realpython.com/python-redis/

https://redis.io/docs/clients/python/


# TODO: determine best way to handle in context of application

'''

try:
    redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)
except redis.exceptions.RedisError as e:
    # TODO: log error e

print(redis_client.ping())