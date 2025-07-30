from __future__ import annotations

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from .config import db_config
from .models import BaseModel
from ..base import AbstractComponent


class DBComponent(AbstractComponent):
    __comp_name__ = "db_comp"

    def __init__(self) -> None:
        self.engine: AsyncEngine = create_async_engine(
            url=db_config.URL,
            pool_pre_ping=True,
        )
        self.session_factory: async_sessionmaker = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    async def on_startup(self) -> None:
        async with self.engine.begin() as conn:
            await conn.run_sync(BaseModel.metadata.create_all)

    async def on_shutdown(self) -> None:
        await self.engine.dispose()
