from aiogram import Dispatcher, F

from .commands import admin_command, start_command
from .common import default_message
from .errors import on_error


def register_handlers(dp: Dispatcher) -> None:
    dp.message.register(start_command, F.text == "/start")
    dp.message.register(admin_command, F.text == "/admin")

    dp.message.register(default_message)

    dp.errors.register(on_error)


__all__ = ["register_handlers"]
