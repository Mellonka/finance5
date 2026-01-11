from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.account.model import Account
from domain.category.model import Category, CategoryID, EnumCategoryStatus
from domain.user.model import User


def _rec(
    parent_id: CategoryID | None,
    categories_by_parent_id: dict[CategoryID | None, list[Category]],
) -> dict:
    categories_hierarchy = dict()
    for child_category in categories_by_parent_id[parent_id]:
        categories_hierarchy[child_category.id] = _rec(child_category.id, categories_by_parent_id)

    return categories_hierarchy


async def handle(*, cur_user: User, db_session: AsyncSession, **_) -> dict:
    categories = await db_session.scalars(
        select(Category).where(
            Account.user_id == cur_user.id,
            Category.status == EnumCategoryStatus.ACTIVE,
        )
    )

    categories_by_parent_id = defaultdict(list)
    for category in categories:
        categories_by_parent_id[category.parent_id].append(category)

    return _rec(None, categories_by_parent_id)
