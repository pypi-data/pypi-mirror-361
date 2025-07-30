import abc


class AbstractComponent(abc.ABC):
    __comp_name__: str

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        if not hasattr(cls, "__comp_name__"):
            raise NotImplementedError(
                f"{cls.__name__} must define class attribute '__comp_name__'"
            )

    @abc.abstractmethod
    async def on_startup(self) -> None: ...

    @abc.abstractmethod
    async def on_shutdown(self) -> None: ...
