from aiogram.types import Message

from ..utils import Localizer


async def default_message(message: Message, localizer: Localizer) -> None:
    text = await localizer("default_message", message=message)
    await message.reply(text)
