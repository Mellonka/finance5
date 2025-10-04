from collections import defaultdict

from sqlalchemy.ext.asyncio import AsyncSession

from domain.category.model import Category, CategoryID
from domain.user.model import UserID
from application.category.cqs.queries.list import handle as list_handle


def _rec(
    parent_id: CategoryID | None,
    categories_by_parent_id: dict[CategoryID | None, list[Category]],
) -> dict:
    categories_hierarchy = dict()
    for child_category in categories_by_parent_id[parent_id]:
        categories_hierarchy[child_category.id] = _rec(child_category.id, categories_by_parent_id)

    return categories_hierarchy


async def handle(*, user_id: UserID, db_session: AsyncSession, **_) -> dict:
    categories = await list_handle(db_session=db_session, user_id=user_id)
    categories_by_parent_id = defaultdict(list)
    for category in categories:
        categories_by_parent_id[category.parent_id].append(category)

    categories_hierarchy = _rec(None, categories_by_parent_id)
    return categories_hierarchy
