from datetime import UTC, datetime

import asyncpg
import sqlalchemy.exc
from sqlalchemy.ext.asyncio import AsyncSession

from application.category.schemas.model import (
    SchemaCategoryDescription,
    SchemaCategoryName,
    SchemaCategoryStatus,
    SchemaCategoryTags,
)
from domain.category.model import Category
from shared.cqs.base import CommandBase
from shared.errors.model import ConflictError


class UpdateCategoryCommandBase(CommandBase):
    def apply(self, category: Category) -> Category:
        raise NotImplementedError


class UpdateCategoryNameCommand(UpdateCategoryCommandBase):
    name: SchemaCategoryName

    def apply(self, category: Category) -> Category:
        category.name = self.name
        return category


class UpdateCategoryDescriptionCommand(UpdateCategoryCommandBase):
    description: SchemaCategoryDescription

    def apply(self, category: Category) -> Category:
        category.description = self.description
        return category


class UpdateCategoryTagsCommand(UpdateCategoryCommandBase):
    tags: SchemaCategoryTags

    def apply(self, category: Category) -> Category:
        category.tags = self.tags
        return category


class UpdateCategoryStatusCommand(UpdateCategoryCommandBase):
    status: SchemaCategoryStatus

    def apply(self, category: Category) -> Category:
        category.status = self.status
        return category


type UpdateCategoryCommand = (
    UpdateCategoryNameCommand
    | UpdateCategoryDescriptionCommand
    | UpdateCategoryTagsCommand
    | UpdateCategoryStatusCommand
)


async def handle(
    *, category: Category, db_session: AsyncSession, commands: list[UpdateCategoryCommand], **_
) -> Category:
    if not commands:
        return category

    db_session.add(category)

    for command in commands:
        command.apply(category)

    category.updated = datetime.now(UTC)

    try:
        await db_session.commit()
    except (asyncpg.UniqueViolationError, sqlalchemy.exc.IntegrityError) as exc:
        raise ConflictError from exc

    return category
