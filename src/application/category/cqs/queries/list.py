from enum import StrEnum, auto

from pydantic import Field
from sqlalchemy import ColumnElement, select
from sqlalchemy.ext.asyncio import AsyncSession

from application.category.schemas.model import (
    SchemaCategoryParentID,
    SchemaCategoryStatus,
    SchemaCategoryTags,
)
from domain.category.model import Category, CategoryID
from domain.user.model import UserID
from shared.cqs.base import QueryBase


class ListCategoryQueryBase(QueryBase):
    def render_filter(self) -> ColumnElement[bool]:
        raise NotImplementedError


class ListCategoryStatusQuery(ListCategoryQueryBase):
    status: SchemaCategoryStatus

    def render_filter(self) -> ColumnElement[bool]:
        return Category.status == self.status


class ListCategoryParentIDQuery(ListCategoryQueryBase):
    parent_id: SchemaCategoryParentID

    def render_filter(self) -> ColumnElement[bool]:
        return Category.parent_id == self.parent_id


class TagsFilterType(StrEnum):
    ALL = auto()
    AT_LEAST_ONE = auto()


class ListCategoryTagsQuery(ListCategoryQueryBase):
    tags: SchemaCategoryTags = Field(default_factory=list)
    filter_type: TagsFilterType = TagsFilterType.ALL

    def render_filter(self) -> ColumnElement[bool]:
        match self.filter_type:
            case TagsFilterType.ALL:
                return Category.tags.contained_by(self.tags)
            case TagsFilterType.AT_LEAST_ONE:
                return Category.tags.overlap(self.tags)

        raise NotImplementedError


type ListCategoryQuery = ListCategoryStatusQuery | ListCategoryTagsQuery | ListCategoryParentIDQuery


async def handle(
    *,
    user_id: UserID,
    db_session: AsyncSession,
    queries: list[ListCategoryQuery] | None = None,
    cursor: CategoryID | None = None,
    limit: int | None = None,
    **_,
) -> list[Category]:
    statement = select(Category).where(Category.user_id == user_id).order_by(Category.id.desc())

    if cursor:
        statement = statement.where(Category.id < cursor)
    if limit is not None:
        statement = statement.limit(limit)
    if queries:
        statement = statement.where(*(q.render_filter() for q in queries))

    return list(await db_session.scalars(statement))
