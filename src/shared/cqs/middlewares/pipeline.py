from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from functools import partial
from itertools import pairwise


@dataclass(slots=True)
class MiddlewareBase(ABC):
    @abstractmethod
    async def handle(self, next_handle: Callable, **kwargs):
        raise NotImplementedError


@dataclass(slots=True)
class MiddlewaresPipeline:
    middlewares: list[MiddlewareBase] = field(default_factory=list)

    _next_handle_cache: dict[int, Callable] = field(default_factory=dict)
    _target_handle_stub: Callable = field(default=int)

    def __post_init__(self):
        for middleware, next_middleware in pairwise(self.middlewares):
            self._next_handle_cache[id(middleware)] = next_middleware.handle

        if self.middlewares:
            self._next_handle_cache[id(self.middlewares[-1])] = self._target_handle_stub

    async def _dispatch_next_handle(self, middleware: MiddlewareBase, target_handle: Callable, **kwargs):
        middleware_id = id(middleware)
        if middleware_id not in self._next_handle_cache:
            raise ValueError('Unknown middleware')

        if self._next_handle_cache[middleware_id] is self._target_handle_stub:
            return await target_handle(**kwargs)

        return await self._next_handle_cache[middleware_id](self.dispatch_next_handle(target_handle), **kwargs)

    def dispatch_next_handle(self, target_handle: Callable) -> Callable:
        return partial(self._dispatch_next_handle, target_handle=target_handle)

    async def handle(self, target_handle: Callable, **kwargs):
        if not self.middlewares:
            return await target_handle(**kwargs)

        return await self.middlewares[0].handle(self.dispatch_next_handle(target_handle), **kwargs)
