import sqlalchemy.exc
from sqlalchemy.ext.asyncio import AsyncSession

from application.category.schemas.model import (
    SchemaCategoryDescription,
    SchemaCategoryName,
    SchemaCategoryParentID,
    SchemaCategoryTags,
)
from domain.category.model import Category
from domain.user.model import UserID
from shared.cqs.command import CommandBase
from shared.errors import ConflictError, NotFoundError
from application.category.cqs.queries.load import auto_handle as load_handle


class CreateCategoryCommand(CommandBase):
    name: SchemaCategoryName
    description: SchemaCategoryDescription
    tags: SchemaCategoryTags
    parent_id: SchemaCategoryParentID
    user_id: UserID


async def handle(*, command: CreateCategoryCommand, db_session: AsyncSession, **_) -> Category:
    if command.parent_id:
        parent_category = await load_handle(db_session=db_session, category_id=command.parent_id)
        if not parent_category or parent_category.user_id != command.user_id:
            raise NotFoundError('Parent category not found')

    if await load_handle(name=command.name, user_id=command.user_id, db_session=db_session):
        raise ConflictError('')

    category = Category(
        name=command.name,
        description=command.description,
        tags=command.tags,
        parent_id=command.parent_id,
        user_id=command.user_id,
    )
    db_session.add(category)

    try:
        await db_session.commit()
    except sqlalchemy.exc.IntegrityError as exc:
        if await load_handle(name=command.name, user_id=command.user_id, db_session=db_session):
            raise ConflictError('') from exc

        raise

    return category
