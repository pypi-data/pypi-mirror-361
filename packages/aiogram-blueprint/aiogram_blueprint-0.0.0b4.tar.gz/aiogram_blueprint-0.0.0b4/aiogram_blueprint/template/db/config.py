from __future__ import annotations

import typing as t
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from ..constants import ENV


@dataclass(frozen=True)
class DBConfig:
    URL: str
    ADAPTER: str
    HOST: t.Optional[str] = None
    PORT: t.Optional[int] = None
    USER: t.Optional[str] = None
    PASSWORD: t.Optional[str] = None
    NAME: t.Optional[str] = None
    PATH: t.Optional[str] = None

    @classmethod
    def load(cls, url: t.Optional[str] = None) -> DBConfig:
        if url is None:
            url = ENV.str("DB_URL")

        parsed = urlparse(url)
        adapter = parsed.scheme
        path = parsed.path.lstrip("/")

        if "sqlite" in adapter:
            db_path = Path(path).resolve()
            db_path.parent.mkdir(parents=True, exist_ok=True)
            return cls(
                URL=url,
                ADAPTER=adapter,
                PATH=path
            )

        return cls(
            URL=url,
            ADAPTER=adapter,
            HOST=parsed.hostname,
            PORT=parsed.port,
            USER=parsed.username,
            PASSWORD=parsed.password,
            NAME=path,
        )


db_config = DBConfig.load()
