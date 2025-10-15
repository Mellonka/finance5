from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from itertools import chain
from typing import Any, AsyncGenerator, Callable, ClassVar
from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.cqs.query.queries import QueryBase, QueryFilterBase, QueryStatementBase
from shared.errors.model import NotFoundError


@dataclass(slots=True)
class QueryHandlerBase[T]:
    entity_cls: type[T]
    load_query_parse: Callable[[dict[str, Any]], QueryFilterBase] | None = None

    _queries: ClassVar[ContextVar[list[QueryFilterBase]]] = ContextVar('_queries', default=[])

    @asynccontextmanager
    async def with_queries(self, queries: list[QueryFilterBase]) -> AsyncGenerator[None, Any]:
        prev_queries = self._queries.get()
        self._queries.set([*prev_queries, *queries])
        try:
            yield
        except Exception:
            raise
        finally:
            self._queries.set(prev_queries)

    def render_statement(self, queries: list[QueryBase], statement: Select[tuple] | None = None) -> Select[tuple[T]]:
        filters = []
        statement = statement or select(self.entity_cls)
        for query in chain(queries, self._queries.get()):
            if isinstance(query, QueryStatementBase):
                statement = query.process_statement(statement)
            else:
                filters.append(query.render_filter())

        return statement.where(*filters)

    async def list(self, *, db_session: AsyncSession, queries: list[QueryBase], **_) -> list[T]:
        return list(await db_session.scalars(self.render_statement(queries)))

    async def load(self, *, db_session: AsyncSession, query: QueryFilterBase | None = None, **kwargs) -> T | None:
        if query is None and self.load_query_parse is not None:
            query = self.load_query_parse(kwargs)

        if query is None or type(query) is QueryFilterBase:
            return None

        return await db_session.scalar(self.render_statement([query]))

    async def load_or_error(self, *, db_session: AsyncSession, query: QueryFilterBase | None = None, **kwargs) -> T:
        entity = await self.load(db_session=db_session, query=query, **kwargs)
        if entity is None:
            raise NotFoundError
        return entity


class QueryHandlerABC[RT](QueryHandlerBase, ABC):
    @abstractmethod
    async def handle(self, **kwargs) -> RT:
        raise NotImplementedError
