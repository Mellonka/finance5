from typing import Any, Callable

from pydantic import TypeAdapter
from sqlalchemy import ColumnElement, and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from application.category.schemas.model import SchemaCategoryID, SchemaCategoryName
from domain.category.model import Category
from domain.user.model import UserID
from shared.cqs.base import QueryBase


class LoadCategoryQueryBase(QueryBase):
    def render_filter(self) -> ColumnElement[bool]:
        raise NotImplementedError


class LoadByCategoryIDQuery(LoadCategoryQueryBase):
    category_id: SchemaCategoryID

    def render_filter(self) -> ColumnElement[bool]:
        return Category.id == self.category_id


class LoadByManyCategoryIDQuery(LoadCategoryQueryBase):
    category_id: list[SchemaCategoryID]

    def render_filter(self) -> ColumnElement[bool]:
        return Category.id.in_(self.category_id)


class LoadByCategoryNameAndUserIDQuery(LoadCategoryQueryBase):
    user_id: UserID
    name: SchemaCategoryName

    def render_filter(self) -> ColumnElement[bool]:
        return and_(Category.name == self.name, Category.user_id == self.user_id)


type LoadCategoryQuery = LoadByCategoryIDQuery | LoadByCategoryNameAndUserIDQuery | LoadCategoryQueryBase
query_parser: Callable[[dict[str, Any]], LoadCategoryQuery] = TypeAdapter(LoadCategoryQuery).validate_python


async def handle(*, db_session: AsyncSession, query: LoadCategoryQuery | None = None, **kwargs) -> Category | None:
    if query is None:
        query = query_parser(kwargs)

    if type(query) is LoadCategoryQueryBase:
        return None

    return await db_session.scalar(select(Category).where(query.render_filter()))
