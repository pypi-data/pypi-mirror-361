from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

T = TypeVar("T", bound=Callable[..., Awaitable])


class _MethodRegistrarMixin:
    """
    Mixin to register methods on a class.
    """

    _registered: dict[str, Callable]

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Initialize registered methods for each subclass."""
        super().__init_subclass__(**kwargs)
        cls._registered = {}

    @classmethod
    def register(cls, func: T, *, name: str | None = None) -> T:
        """Decorator: attach *func* to a class"""
        method_name = name or func.__name__

        # check if the function already exists in the class
        if hasattr(cls, method_name):
            raise AttributeError(
                f"Method '{method_name}' already exists on {cls.__name__}"
            )

        # register the function
        cls._registered[method_name] = func
        setattr(cls, method_name, func)
        return func
