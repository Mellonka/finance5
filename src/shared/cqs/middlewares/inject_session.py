from collections.abc import Callable
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import async_sessionmaker

from shared.cqs.middlewares.pipeline import MiddlewareBase


@dataclass(slots=True)
class InjectSessionMiddleware(MiddlewareBase):
    session_maker: async_sessionmaker

    async def handle(self, next_handle: Callable, **kwargs):
        async with self.session_maker() as db_session:
            return await next_handle(self, db_session=db_session, **kwargs)
