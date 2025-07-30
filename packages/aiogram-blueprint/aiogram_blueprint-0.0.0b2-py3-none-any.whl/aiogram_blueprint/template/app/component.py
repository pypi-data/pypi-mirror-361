from __future__ import annotations

from fastapi import FastAPI

from .routes import add_routes
from ..base import AbstractComponent


class AppComponent(AbstractComponent):
    __comp_name__ = "app_comp"

    def __init__(self) -> None:
        self.app = FastAPI()

    async def on_startup(self) -> None:
        add_routes(self.app)

    async def on_shutdown(self) -> None:
        pass
