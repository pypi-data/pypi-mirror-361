import asyncio
from aiogram import Bot, Dispatcher

from . import ComponentRegistry
from .bot import BotComponent
from .db import DBComponent
from .redis import RedisComponent
from .utils import resolve_component_attr

registry = ComponentRegistry()


def setup_components():
    registry.register(RedisComponent)
    registry.register(DBComponent)
    registry.register(
        BotComponent,
        depends_on=[DBComponent],
    )


async def main() -> None:
    setup_components()
    dp: Dispatcher = resolve_component_attr(BotComponent, "dp")
    bot: Bot = resolve_component_attr(BotComponent, "bot")

    dp.startup.register(registry.startup_all)
    dp.shutdown.register(registry.shutdown_all)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
