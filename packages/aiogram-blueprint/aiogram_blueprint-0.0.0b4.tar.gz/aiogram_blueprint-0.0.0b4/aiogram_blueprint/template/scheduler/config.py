from __future__ import annotations

import typing as t
from dataclasses import dataclass
from urllib.parse import urlparse

from ..constants import ENV


@dataclass(frozen=True)
class SchedulerConfig:
    HOST: str
    PORT: int
    DB: int
    USER: t.Optional[str] = None
    PASSWORD: t.Optional[str] = None

    @classmethod
    def load(cls, redis_url: t.Optional[str] = None) -> SchedulerConfig:
        if redis_url is None:
            redis_url = ENV.str("REDIS_URL")

        parsed = urlparse(redis_url)
        db = int(parsed.path.lstrip("/")) if parsed.path else 0

        return cls(
            HOST=parsed.hostname or "localhost",
            PORT=parsed.port or 6379,
            DB=db + 1,
            USER=parsed.username,
            PASSWORD=parsed.password,
        )


scheduler_config = SchedulerConfig.load()
