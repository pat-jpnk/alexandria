import redis

'''
https://pypi.org/project/redis/

https://realpython.com/python-redis/

https://redis.io/docs/clients/python/



'''

redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)

print(redis_client.ping())