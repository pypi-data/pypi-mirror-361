import typing as t

from apscheduler.jobstores.base import BaseJobStore
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from .config import scheduler_config
from ..base import AbstractComponent
from ..constants import TIMEZONE

DEFAULT_JOBSTORE = "default"


class SchedulerComponent(AbstractComponent):
    __comp_name__ = "scheduler_comp"

    def __init__(self) -> None:
        name, store = self._create_default_jobstore()

        self.jobstores: t.Dict[str, BaseJobStore] = {name: store}
        self.scheduler: AsyncIOScheduler = AsyncIOScheduler(
            jobstores=self.jobstores,
            timezone=TIMEZONE,
        )

    async def on_startup(self) -> None:
        self.scheduler.start()

    async def on_shutdown(self) -> None:
        self.scheduler.shutdown(wait=False)

    @classmethod
    def _create_default_jobstore(cls) -> t.Tuple[str, BaseJobStore]:
        return DEFAULT_JOBSTORE, RedisJobStore(
            db=scheduler_config.DB + 1,
            host=scheduler_config.HOST,
            port=scheduler_config.PORT,
            password=scheduler_config.PASSWORD,
            username=scheduler_config.USER,
        )
