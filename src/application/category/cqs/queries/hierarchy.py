from collections import defaultdict

from sqlalchemy.ext.asyncio import AsyncSession

from domain.category.model import Category, CategoryID
from application.category.cqs.queries.load import load_query_parse
from shared.cqs.query.handler import QueryHandlerABC


def _rec(
    parent_id: CategoryID | None,
    categories_by_parent_id: dict[CategoryID | None, list[Category]],
) -> dict:
    categories_hierarchy = dict()
    for child_category in categories_by_parent_id[parent_id]:
        categories_hierarchy[child_category.id] = _rec(child_category.id, categories_by_parent_id)

    return categories_hierarchy


class HierarchyHandler(QueryHandlerABC):
    async def handle(self, *, db_session: AsyncSession, **_) -> dict:
        categories = await self.list(db_session=db_session, queries=[])
        categories_by_parent_id = defaultdict(list)
        for category in categories:
            categories_by_parent_id[category.parent_id].append(category)

        categories_hierarchy = _rec(None, categories_by_parent_id)
        return categories_hierarchy


handler = HierarchyHandler(Category, load_query_parse)
