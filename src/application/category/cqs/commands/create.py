import sqlalchemy.exc
from sqlalchemy.ext.asyncio import AsyncSession

from application.category.errors import CategoryIntegrityError
from application.category.schemas.model import (
    SchemaCategoryCode,
    SchemaCategoryDescription,
    SchemaCategoryParentID,
    SchemaCategoryTags,
    SchemaCategoryTitle,
)
from domain.category.model import Category
from domain.user.model import User
from shared.cqs.command import CommandBase
from shared.cqs.parser import auto_parse_kwargs


class CreateCategoryCommand(CommandBase):
    code: SchemaCategoryCode
    title: SchemaCategoryTitle
    description: SchemaCategoryDescription
    tags: SchemaCategoryTags
    parent_id: SchemaCategoryParentID


@auto_parse_kwargs(command_type=CreateCategoryCommand)
async def handle(
    *,
    cur_user: User,
    db_session: AsyncSession,
    command: CreateCategoryCommand,
    **_,
) -> Category:
    category = Category(
        code=command.code,
        title=command.title,
        description=command.description,
        tags=command.tags,
        parent_id=command.parent_id,
        user_id=cur_user.id,
    )
    db_session.add(category)

    try:
        await db_session.commit()
    except sqlalchemy.exc.IntegrityError as exc:
        raise CategoryIntegrityError from exc

    return category
