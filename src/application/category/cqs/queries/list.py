from typing import Any, Literal, get_args
from sqlalchemy import ColumnElement, not_, select
from sqlalchemy.ext.asyncio import AsyncSession

from application.category.schemas.model import (
    SchemaCategoryID,
    SchemaCategoryName,
    SchemaCategoryStatus,
    SchemaCategoryTags,
)
from application.user.schemas.model import SchemaUserID
from domain.category.model import Category
from shared.cqs.parser import auto_parse_kwargs
from shared.cqs.query import QueryFilterBase, apply_queries


class CategoryStatusQuery(QueryFilterBase):
    status: SchemaCategoryStatus | list[SchemaCategoryStatus]

    def render_filter(self) -> ColumnElement[bool]:
        if isinstance(self.status, list):
            return Category.status.in_(self.status)
        return Category.status == self.status


class CategoryTagsQuery(QueryFilterBase):
    tags: SchemaCategoryTags
    filter_type: Literal['HAVE_ANY', 'HAVE_ALL', 'HAVE_NOTHING', 'HAVE_SAME'] = 'HAVE_ALL'

    def render_filter(self) -> ColumnElement[bool]:
        match self.filter_type:
            case 'HAVE_ALL':
                return Category.tags.contains(self.tags)
            case 'HAVE_ANY':
                return Category.tags.overlap(self.tags)
            case 'HAVE_NOTHING':
                return not_(Category.tags.overlap(self.tags))
            case 'HAVE_SAME':
                return Category.tags == self.tags

        raise ValueError(f'Unknown filter_type={self.filter_type}')


class CategoryNameQuery(QueryFilterBase):
    name: SchemaCategoryName | list[SchemaCategoryName]

    def render_filter(self) -> ColumnElement[bool]:
        if isinstance(self.name, list):
            return Category.name.in_(self.name)
        return Category.name == self.name


class CategoryIDQuery(QueryFilterBase):
    category_id: SchemaCategoryID | list[SchemaCategoryID]

    def render_filter(self) -> ColumnElement[bool]:
        if isinstance(self.category_id, list):
            return Category.id.in_(self.category_id)
        return Category.id == self.category_id


class CategoryUserIDQuery(QueryFilterBase):
    user_id: SchemaUserID | list[SchemaUserID]

    def render_filter(self) -> ColumnElement[bool]:
        if isinstance(self.user_id, list):
            return Category.user_id.in_(self.user_id)
        return Category.user_id == self.user_id


class CategoryParentIDQuery(QueryFilterBase):
    parent_id: SchemaCategoryID | list[SchemaCategoryID]

    def render_filter(self) -> ColumnElement[bool]:
        if isinstance(self.parent_id, list):
            return Category.parent_id.in_(self.parent_id)
        return Category.parent_id == self.parent_id


ListCategoryQuery = (
    CategoryStatusQuery
    | CategoryTagsQuery
    | CategoryIDQuery
    | CategoryNameQuery
    | CategoryUserIDQuery
    | CategoryParentIDQuery
)


async def handle(*, db_session: AsyncSession, queries: list[ListCategoryQuery], **_) -> list[Category]:
    return list(await db_session.scalars(apply_queries(select(Category), *queries)))


@auto_parse_kwargs(query_types=get_args(ListCategoryQuery))
async def auto_handle(**kwargs: Any) -> list[Category]:
    return await handle(**kwargs)
