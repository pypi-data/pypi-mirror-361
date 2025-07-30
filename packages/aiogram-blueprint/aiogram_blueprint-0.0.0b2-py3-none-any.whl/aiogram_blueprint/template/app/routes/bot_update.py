from aiogram.types import Update
from starlette.responses import Response

from ...bot import BotComponent
from ...utils import resolve_component


async def bot_update(update: dict) -> Response:
    bot_comp: BotComponent = resolve_component(BotComponent)

    await bot_comp.dp.feed_update(
        bot=bot_comp.bot,
        update=Update(**update),
    )
    return Response()
