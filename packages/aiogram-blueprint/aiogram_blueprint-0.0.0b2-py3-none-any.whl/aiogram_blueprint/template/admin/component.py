from __future__ import annotations

import typing as t

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine
from starlette_admin import I18nConfig
from starlette_admin.contrib.sqla import Admin

from .config import admin_config
from .views import add_views
from ..app import AppComponent
from ..base import AbstractComponent
from ..constants import DEFAULT_LOCALE
from ..db import DBComponent
from ..utils import resolve_component_attr


class AdminComponent(AbstractComponent):
    __comp_name__ = "admin_comp"

    def __init__(self) -> None:
        self.app = self.resolve_app()
        self.admin = Admin(
            engine=self.resolve_engine(),
            templates_dir=str(admin_config.TEMPLATES_DIR),
            i18n_config=I18nConfig(
                default_locale=DEFAULT_LOCALE,
            ),
        )

    @staticmethod
    def resolve_app() -> FastAPI:
        app: t.Optional[FastAPI] = resolve_component_attr(
            AppComponent,
            attr="app",
        )
        if app is None:
            raise RuntimeError("App component is not registered")
        return app

    @staticmethod
    def resolve_engine() -> AsyncEngine:
        engine: t.Optional[AsyncEngine] = resolve_component_attr(
            DBComponent,
            attr="engine",
        )
        if engine is None:
            raise RuntimeError("DB component is not registered")
        return engine

    async def on_startup(self) -> None:
        self.admin.mount_to(self.app)
        add_views(self.admin)

    async def on_shutdown(self) -> None:
        pass
