from typing import Any, get_args

import asyncpg
import sqlalchemy.exc
from sqlalchemy.ext.asyncio import AsyncSession

from application.category.cqs.queries.load import load_category
from application.category.errors import CategoryConflictError, CategoryNotFoundError
from application.category.schemas.model import (
    SchemaCategoryCode,
    SchemaCategoryDescription,
    SchemaCategoryStatus,
    SchemaCategoryTags,
    SchemaCategoryTitle,
)
from domain.category.model import Category
from shared.cqs.command import CommandBase
from shared.cqs.parser import auto_parse_kwargs


class UpdateCategoryCodeCommand(CommandBase):
    code: SchemaCategoryCode

    def apply(self, category: Category) -> Category:
        category.code = self.code
        return category


class UpdateCategoryTitleCommand(CommandBase):
    title: SchemaCategoryTitle

    def apply(self, category: Category) -> Category:
        category.title = self.title
        return category


class UpdateCategoryDescriptionCommand(CommandBase):
    description: SchemaCategoryDescription

    def apply(self, category: Category) -> Category:
        category.description = self.description
        return category


class UpdateCategoryTagsCommand(CommandBase):
    tags: SchemaCategoryTags

    async def apply(self, category: Category) -> Category:
        category.tags = self.tags
        return category


class UpdateCategoryStatusCommand(CommandBase):
    status: SchemaCategoryStatus

    def apply(self, category: Category) -> Category:
        category.status = self.status
        return category


UpdateCategoryCommand = (
    UpdateCategoryCodeCommand
    | UpdateCategoryTitleCommand
    | UpdateCategoryDescriptionCommand
    | UpdateCategoryTagsCommand
    | UpdateCategoryStatusCommand
)


@load_category()
@auto_parse_kwargs(command_types=get_args(UpdateCategoryCommand))
async def handle(
    *,
    category: Category | None,
    db_session: AsyncSession,
    commands: list[UpdateCategoryCommand],
    **_,
) -> Category:
    if category is None:
        raise CategoryNotFoundError

    for command in commands:
        command.apply(category)

    try:
        await db_session.commit()
    except sqlalchemy.exc.IntegrityError as exc:
        if isinstance(exc.orig, asyncpg.UniqueViolationError):
            raise CategoryConflictError from exc
        raise

    return category


async def auto_handle(**kwargs: Any) -> Category:
    return await handle(**kwargs)
