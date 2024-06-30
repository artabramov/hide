"""Redis cache creator."""

import redis.asyncio as redis
from app.config import get_config

cfg = get_config()


async def get_cache():
    """Return SQLAlchemy session object."""
    try:
        conn = redis.Redis(host=cfg.REDIS_HOST, port=cfg.REDIS_PORT,
                           decode_responses=cfg.REDIS_DECODE)
        yield conn
    finally:
        await conn.close()
