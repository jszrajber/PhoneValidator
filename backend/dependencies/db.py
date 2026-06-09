from backend.db.session import AsyncSessionLocal
from backend.core.config import settings
import redis.asyncio as redis

redis_pool = redis.ConnectionPool.from_url(
    settings.REDIS_URL,
    decode_responses=True,
    socket_connect_timeout=5,
    socket_timeout=5
)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


async def get_redis():
    async with redis.Redis(connection_pool=redis_pool) as client:
        yield client
