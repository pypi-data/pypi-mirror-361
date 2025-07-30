from fastapi import FastAPI

from .bot_update import bot_update
from ...bot.config import bot_config


def add_routes(app: FastAPI) -> None:
    app.add_api_route(
        path=f"/{bot_config.WEBHOOK_PATH}",
        endpoint=bot_update,
        methods=["POST"],
    )


__all__ = ["add_routes"]
