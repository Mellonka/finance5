from abc import ABC
from typing import Any

from shared.errors.model import NotFoundError



class SqlAlchemyRepository(RepositoryABC):
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
