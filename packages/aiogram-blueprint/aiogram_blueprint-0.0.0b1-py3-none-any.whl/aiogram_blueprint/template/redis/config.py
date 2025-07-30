from __future__ import annotations

import typing as t
from dataclasses import dataclass
from urllib.parse import urlparse

from ..constants import ENV


@dataclass(frozen=True)
class RedisConfig:
    URL: str
    HOST: str
    PORT: int
    DB: int
    USER: t.Optional[str] = None
    PASSWORD: t.Optional[str] = None

    @classmethod
    def load(cls, url: t.Optional[str] = None) -> RedisConfig:
        if url is None:
            url = ENV.str("REDIS_URL")

        parsed = urlparse(url)

        return cls(
            URL=url,
            HOST=parsed.hostname or "localhost",
            PORT=parsed.port or 6379,
            DB=int(parsed.path.lstrip("/")) if parsed.path else 0,
            USER=parsed.username,
            PASSWORD=parsed.password,
        )


redis_config = RedisConfig.load()
