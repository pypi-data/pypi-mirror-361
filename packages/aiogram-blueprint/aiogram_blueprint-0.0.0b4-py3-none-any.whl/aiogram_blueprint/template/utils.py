import typing as t

from .base import AbstractComponent
from .registry import COMPONENTS_REGISTRY

_TComponent = t.TypeVar("_TComponent", bound=AbstractComponent)


def resolve_component(component_cls: t.Type[_TComponent]) -> _TComponent:
    component_name = component_cls.__comp_name__
    components = COMPONENTS_REGISTRY.get()
    component = components.get(component_name)

    if component is None:
        raise ValueError(
            f"Component '{component_name}' not found in current context."
        )

    return component


def resolve_component_attr(component_cls: t.Type[_TComponent], attr: str) -> t.Any:
    component = resolve_component(component_cls)
    if not hasattr(component, attr):
        raise AttributeError(
            f"Component '{component.__comp_name__}' has no attribute '{attr}'."
        )

    return getattr(component, attr)
