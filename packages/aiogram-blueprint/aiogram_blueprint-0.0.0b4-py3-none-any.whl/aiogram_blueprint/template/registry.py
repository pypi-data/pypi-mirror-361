import typing as t
from contextvars import ContextVar

from .base import AbstractComponent

COMPONENTS_REGISTRY: ContextVar[t.Dict[str, t.Any]] = ContextVar(
    "components_registry", default={}
)


class ComponentRegistry:

    def __init__(self) -> None:
        self.components: t.Dict[str, AbstractComponent] = {}
        self.dependencies: t.Dict[str, t.List[str]] = {}
        self.startup_order: t.List[str] = []

    async def startup_all(self) -> None:
        self.startup_order = await self._resolve_startup_order()
        for name in self.startup_order:
            component = self.components[name]
            await component.on_startup()

    async def shutdown_all(self) -> None:
        for name in reversed(self.startup_order):
            await self.components[name].on_shutdown()

    @staticmethod
    def _register_global(component: AbstractComponent) -> None:
        components = COMPONENTS_REGISTRY.get().copy()
        components[component.__comp_name__] = component
        COMPONENTS_REGISTRY.set(components)

    def register(
            self,
            component_cls: t.Type[AbstractComponent],
            depends_on: t.Optional[t.List[t.Type[AbstractComponent]]] = None,
    ) -> None:
        name = component_cls.__comp_name__
        component = component_cls()

        if name in self.components:
            raise ValueError(f"Component {name} already registered")

        self.components[name] = component
        self._register_global(component)

        dependencies = [dep.__comp_name__ for dep in depends_on or []]
        self.dependencies[name] = dependencies

    async def _resolve_startup_order(self) -> t.List[str]:
        visited = set()
        temp_mark = set()
        order = []

        async def visit(_name: str):
            if _name in visited:
                return
            if _name in temp_mark:
                raise RuntimeError(f"Cyclic dependency detected at {_name}")

            temp_mark.add(_name)
            for dep_name in self.dependencies.get(_name, []):
                if dep_name not in self.components:
                    raise ValueError(
                        f"Dependency {dep_name} not registered for {_name}"
                    )
                await visit(dep_name)

            temp_mark.remove(_name)
            visited.add(_name)
            order.append(_name)

        for name in self.components:
            await visit(name)

        return order
