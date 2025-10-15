from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from itertools import chain
from typing import Any, ClassVar, Generator
from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.cqs.query.queries import QueryBase, QueryFilterBase, QueryStatementBase
from shared.errors.model import NotFoundError


@dataclass(slots=True)
class Repository[T]:
    _entity_cls: type[T] = field(init=False)
    _queries: ClassVar[ContextVar[list[QueryFilterBase]]] = ContextVar('_queries', default=[])

    @classmethod
    def load_query_parse(cls, kwargs: dict[str, Any]) -> QueryFilterBase | None:
        return None

    @contextmanager
    def with_queries(self, queries: list[QueryFilterBase]) -> Generator[None, Any]:
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
        statement = statement or select(self._entity_cls)
        for query in chain(queries, self._queries.get()):
            if isinstance(query, QueryStatementBase):
                statement = query.process_statement(statement)
            else:
                filters.append(query.render_filter())

        return statement.where(*filters)

    async def list(self, *, db_session: AsyncSession, queries: list[QueryBase], **_) -> list[T]:
        return list(await db_session.scalars(self.render_statement(queries)))

    async def load(self, *, db_session: AsyncSession, query: QueryFilterBase | None = None, **kwargs) -> T | None:
        if query is None:
            query = self.load_query_parse(kwargs)

        if query is None or type(query) is QueryFilterBase:
            return None

        return await db_session.scalar(self.render_statement([query]))

    async def load_or_error(self, *, db_session: AsyncSession, query: QueryFilterBase | None = None, **kwargs) -> T:
        if entity := await self.load(db_session=db_session, query=query, **kwargs):
            return entity
        raise NotFoundError
