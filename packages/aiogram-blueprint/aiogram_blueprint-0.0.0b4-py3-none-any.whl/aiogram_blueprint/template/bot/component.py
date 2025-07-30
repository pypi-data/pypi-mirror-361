from __future__ import annotations

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.base import BaseStorage, DefaultKeyBuilder
from aiogram.fsm.storage.redis import RedisStorage
from sulguk import SULGUK_PARSE_MODE

from .config import bot_config
from .handlers import register_handlers
from .middlewares import register_middlewares
from ..base import AbstractComponent
from ..redis import RedisComponent
from ..utils import resolve_component_attr


class BotComponent(AbstractComponent):
    __comp_name__ = "bot_comp"

    def __init__(self) -> None:
        self.bot = Bot(
            token=bot_config.TOKEN,
            default=DefaultBotProperties(
                parse_mode=SULGUK_PARSE_MODE,
            ),
        )
        self.storage = self._create_storage()
        self.dp = Dispatcher(storage=self.storage)

    async def on_startup(self) -> None:
        register_middlewares(self.dp, self.bot)
        register_handlers(self.dp)
        await self.setup_commands()
        await self.bot.set_webhook(bot_config.WEBHOOK_URL)

    async def on_shutdown(self) -> None:
        await self.delete_commands()
        await self.bot.delete_webhook()
        await self.bot.session.close()

    async def setup_commands(self) -> None:
        pass

    async def delete_commands(self) -> None:
        pass

    @classmethod
    def _create_storage(cls) -> BaseStorage:
        redis = resolve_component_attr(RedisComponent, "redis")
        return RedisStorage(
            redis=redis,
            key_builder=DefaultKeyBuilder(with_destiny=True),
        )
