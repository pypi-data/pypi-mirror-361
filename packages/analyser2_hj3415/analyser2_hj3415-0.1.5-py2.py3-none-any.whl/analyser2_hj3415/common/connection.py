import os, redis

# 싱글톤 클라이언트 정의
REDIS_HOST = os.getenv('REDIS_HOST')
client: redis.Redis = None

def get_redis_client(port: int = 6379) -> redis.Redis:
    global client
    if client is None:
        client = redis.Redis(host=REDIS_HOST, port=port,
                            decode_responses=True)
    return client
