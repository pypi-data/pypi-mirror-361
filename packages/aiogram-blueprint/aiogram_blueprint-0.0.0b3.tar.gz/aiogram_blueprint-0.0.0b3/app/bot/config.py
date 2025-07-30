import typing as t
from dataclasses import dataclass

from ..constants import ENV


@dataclass(frozen=True)
class BotConfig:
    TOKEN: str
    USERNAME: str
    DEV_ID: int
    ADMINS: t.List[int]

    @classmethod
    def load(cls) -> "BotConfig":
        token = ENV.str("BOT_TOKEN")
        username = ENV.str("BOT_USERNAME")
        dev_id = ENV.int("BOT_DEV_ID")
        admins = ENV.list("BOT_ADMINS", subcast=int, default=[])

        return cls(
            TOKEN=token,
            USERNAME=username,
            DEV_ID=dev_id,
            ADMINS=admins,
        )


bot_config = BotConfig.load()