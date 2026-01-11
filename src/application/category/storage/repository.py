import functools
from typing import ClassVar
from uuid import UUID

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.category.model import Category
from shared.storage.filters import FilterHandler, UseInForArrays
from shared.storage.repository import RepositoryBase, RepositoryConfig


class CategoryUseInForArrays(UseInForArrays[Category]):
    blacklist: ClassVar = {Category.tags}


class CategoryFilterHandler(FilterHandler[Category]):
    @classmethod
    def category_id(
        cls, entity_cls: type[Category], statement: Select[tuple[Category]], value: list[UUID] | UUID
    ) -> Select[tuple[Category]]:
        if isinstance(value, list | tuple):
            return statement.where(Category.id.in_(value))
        return statement.where(Category.id == value)


class CategoryRepository(
    RepositoryBase[Category],
    config=RepositoryConfig(
        entity_cls=Category,
        primary_key=Category.id,
        filter_handlers=[CategoryUseInForArrays, CategoryFilterHandler],
    ),
):
    def list_hierarchy(self) -> dict: ...


def make_category_repo(func):
    @functools.wraps(func)
    async def wrapper(*, db_session: AsyncSession, **kwargs):
        if 'category_repo' not in kwargs:
            kwargs['category_repo'] = CategoryRepository(db_session)
        return await func(db_session=db_session, **kwargs)

    return wrapper
