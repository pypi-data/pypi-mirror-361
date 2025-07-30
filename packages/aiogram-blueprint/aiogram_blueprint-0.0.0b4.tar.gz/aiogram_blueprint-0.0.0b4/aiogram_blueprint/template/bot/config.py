from __future__ import annotations

import typing as t
from dataclasses import dataclass

from ..app.config import app_config
from ..constants import ENV


@dataclass(frozen=True)
class BotConfig:
    TOKEN: str
    USERNAME: str
    DEV_ID: int
    ADMINS: t.List[int]
    WEBHOOK_PATH: str
    WEBHOOK_URL: str

    @classmethod
    def load(cls) -> BotConfig:
        token = ENV.str("BOT_TOKEN")
        username = ENV.str("BOT_USERNAME")
        dev_id = ENV.int("BOT_DEV_ID")
        admins = ENV.list("BOT_ADMINS", subcast=int, default=[])

        webhook_path = f"{username}/{token}"
        webhook_url = f"{app_config.URL.rstrip('/')}/{webhook_path}"

        return cls(
            TOKEN=token,
            USERNAME=username,
            DEV_ID=dev_id,
            ADMINS=admins,
            WEBHOOK_PATH=webhook_path,
            WEBHOOK_URL=webhook_url,
        )


bot_config = BotConfig.load()
