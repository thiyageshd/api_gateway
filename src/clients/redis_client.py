import redis.asyncio as redis
from config import Config

class RedisClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RedisClient, cls).__new__(cls)
            cls._instance.redis = None
        return cls._instance

    async def initialize(self):
        """Initialize the Redis connection asynchronously."""
        if self.redis is None:
            self.redis = await redis.from_url(
                f"redis://{Config.REDIS_HOST}:{Config.REDIS_PORT}/{Config.REDIS_DB}",
                encoding="utf-8",
                decode_responses=True
            )

    async def get_redis(self):
        """Ensure Redis is initialized before returning the instance."""
        if self.redis is None:
            await self.initialize()
        return self.redis

# Create Singleton Instance
redis_client = RedisClient()
