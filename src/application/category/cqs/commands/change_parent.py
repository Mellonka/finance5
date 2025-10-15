from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from application.category.cqs.commands.update import UpdateCategoryCommandBase
from application.category.schemas.model import SchemaCategoryParentID
from domain.category.model import Category
from shared.errors.model import NotFoundError
from application.category.cqs.queries.load import handler


class CategoryChangeParentCommand(UpdateCategoryCommandBase):
    parent_id: SchemaCategoryParentID


async def handle(
    *, category: Category, db_session: AsyncSession, command: CategoryChangeParentCommand, **_
) -> Category:
    if command.parent_id:
        parent_category = await handler.load(db_session=db_session, category_id=command.parent_id)
        if not parent_category or parent_category.user_id != category.user_id:
            raise NotFoundError('Parent category not found')

    db_session.add(category)

    category.parent_id = command.parent_id
    category.updated = datetime.now(UTC)

    await db_session.commit()

    return category
