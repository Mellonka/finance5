from datetime import datetime
from typing import Any, get_args

from sqlalchemy.ext.asyncio import AsyncSession

from application.category.cqs.queries.load import auto_handle as load_handle
from application.category.schemas.model import (
    SchemaCategoryDescription,
    SchemaCategoryID,
    SchemaCategoryName,
    SchemaCategoryStatus,
    SchemaCategoryTags,
)
from domain.category.model import Category, EnumCategoryStatus
from shared.cqs.command import CommandBase
from shared.cqs.parser import auto_parse_kwargs
from shared.errors import ConflictError
from shared.errors.domain import DomainError, NotFoundError


class UpdateCategoryNameCommand(CommandBase):
    name: SchemaCategoryName

    async def check_command(self, category: Category, db_session: AsyncSession) -> DomainError | None:
        if self.name != category.name and await load_handle(
            db_session=db_session, user_id=category.user_id, name=self.name
        ):
            return ConflictError('Category with that name already exists')

    async def apply(self, category: Category, db_session: AsyncSession) -> Category:
        if error := await self.check_command(category, db_session):
            raise error

        category.name = self.name
        return category


class UpdateCategoryDescriptionCommand(CommandBase):
    description: SchemaCategoryDescription

    async def apply(self, category: Category, _: AsyncSession) -> Category:
        category.description = self.description
        return category


class UpdateCategoryTagsCommand(CommandBase):
    tags: SchemaCategoryTags

    async def apply(self, category: Category, _: AsyncSession) -> Category:
        category.tags = self.tags
        return category


class UpdateCategoryStatusCommand(CommandBase):
    status: SchemaCategoryStatus
    cascade: bool = False

    async def checks(self, category: Category, db_session: AsyncSession) -> DomainError | None:
        if self.cascade:
            return

        if self.status == EnumCategoryStatus.DISABLED:
            ...
            # child_categories = await list_handle(db_session=db_session, parent_id=category.id)

    async def apply(self, category: Category, db_session: AsyncSession) -> Category:
        if error := await self.checks(category, db_session):
            raise error

        category.status = self.status
        return category


class UpdateCategoryParentCommand(CommandBase):
    parent_id: SchemaCategoryID | None

    async def checks(self, category: Category, db_session: AsyncSession) -> DomainError | None:
        if not self.parent_id:
            return

        if category.id == self.parent_id:
            return ConflictError('Category cannot be a parent for itself')

        parent_category = await load_handle(db_session=db_session, category_id=self.parent_id)
        if not parent_category or parent_category.user_id != category.user_id:
            return NotFoundError('Parent category not found')

        while parent_category and parent_category.parent_id and parent_category.parent_id != category.id:
            parent_category = await load_handle(db_session=db_session, category_id=parent_category.parent_id)

        if parent_category and parent_category.parent_id == category.id:
            return ConflictError('Cyclic hierarchies of categories are not allowed')

    async def apply(self, category: Category, db_session: AsyncSession) -> Category:
        if error := await self.checks(category, db_session):
            raise error

        category.parent_id = self.parent_id
        return category


UpdateCategoryCommand = (
    UpdateCategoryNameCommand
    | UpdateCategoryDescriptionCommand
    | UpdateCategoryTagsCommand
    | UpdateCategoryStatusCommand
)


async def handle(
    *, category: Category, db_session: AsyncSession, commands: list[UpdateCategoryCommand], **_
) -> Category:
    db_session.add(category)

    for command in commands:
        await command.apply(category, db_session)

    category.updated = datetime.now()
    await db_session.commit()

    return category


@auto_parse_kwargs(command_types=get_args(UpdateCategoryCommand))
async def auto_handle(**kwargs: Any) -> Category:
    return await handle(**kwargs)
