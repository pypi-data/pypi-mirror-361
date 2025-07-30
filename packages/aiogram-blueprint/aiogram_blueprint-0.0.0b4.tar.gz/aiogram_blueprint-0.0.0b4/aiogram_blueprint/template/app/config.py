from __future__ import annotations

from dataclasses import dataclass

from ..constants import ENV


@dataclass(frozen=True)
class AppConfig:
    URL: str
    HOST: str
    PORT: int

    @classmethod
    def load(cls) -> AppConfig:
        return cls(
            URL=ENV.str("APP_URL"),
            HOST=ENV.str("APP_HOST"),
            PORT=ENV.int("APP_PORT")
        )


app_config = AppConfig.load()
