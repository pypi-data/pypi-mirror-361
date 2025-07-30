import typing as t
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from . import ComponentRegistry
from .admin import AdminComponent
from .app import AppComponent
from .bot import BotComponent
from .db import DBComponent
from .redis import RedisComponent
from .scheduler import SchedulerComponent
from .utils import resolve_component_attr

registry = ComponentRegistry()


@asynccontextmanager
async def lifespan(_: FastAPI) -> t.AsyncGenerator:
    await registry.startup_all()
    yield
    await registry.shutdown_all()


def main() -> None:
    registry.register(RedisComponent)
    registry.register(DBComponent)

    registry.register(
        SchedulerComponent,
        depends_on=[RedisComponent],
    )
    registry.register(
        BotComponent,
        depends_on=[
            SchedulerComponent,
            DBComponent,
        ]
    )
    registry.register(
        AppComponent,
        depends_on=[BotComponent],
    )
    registry.register(
        AdminComponent,
        depends_on=[AppComponent],
    )

    app: FastAPI = resolve_component_attr(AppComponent, "app")
    app.router.lifespan_context = lifespan  # type: ignore
    from .app.config import app_config

    uvicorn.run(
        app=app,
        host=app_config.HOST,
        port=app_config.PORT,
        forwarded_allow_ips="*",
        proxy_headers=True,
    )


if __name__ == "__main__":
    main()
