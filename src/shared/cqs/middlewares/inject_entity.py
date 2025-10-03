from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from functools import wraps
from typing import Any

from shared.cqs.middlewares.pipeline import MiddlewareBase


@dataclass(slots=True)
class InjectEntityMiddleware(MiddlewareBase):
    load_handle: Callable

    async def handle(self, next_handle: Callable, **kwargs):
        return await next_handle(self, **kwargs, **await self.load_handle(**kwargs))


class InjectEntityDecorator[T](ABC):
    async def __call__(self, func) -> Any:
        @wraps
        async def wrap(*args, **kwargs):
            return await func(*args, **await self.load_entity(*args, **kwargs))

        return wrap

    @abstractmethod
    async def load_entity(self, *args, **kwargs) -> dict[str, T]:
        raise NotImplementedError
