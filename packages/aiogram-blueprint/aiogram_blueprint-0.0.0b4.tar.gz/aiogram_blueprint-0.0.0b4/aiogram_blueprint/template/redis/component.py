from __future__ import annotations

from redis.asyncio import Redis

from .config import redis_config
from ..base import AbstractComponent


class RedisComponent(AbstractComponent):
    __comp_name__ = "redis_comp"

    def __init__(self) -> None:
        self.redis = Redis.from_url(url=redis_config.URL)

    async def on_startup(self) -> None:
        await self.redis.ping()

    async def on_shutdown(self) -> None:
        await self.redis.aclose()
