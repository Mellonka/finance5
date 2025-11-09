from typing import Any
from sqlalchemy import ColumnElement, and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from application.category.schemas.model import SchemaCategoryID, SchemaCategoryName
from application.user.schemas.model import SchemaUserID
from domain.category.model import Category
from shared.cqs.parser import auto_parse_kwargs
from shared.cqs.query import QueryFilterBase, apply_queries


class LoadByCategoryIDQuery(QueryFilterBase):
    Category_id: SchemaCategoryID

    def render_filter(self) -> ColumnElement[bool]:
        return Category.id == self.Category_id


class LoadByCategoryNameQuery(QueryFilterBase):
    user_id: SchemaUserID
    name: SchemaCategoryName

    def render_filter(self) -> ColumnElement[bool]:
        return and_(Category.name == self.name, Category.user_id == self.user_id)


LoadCategoryQuery = LoadByCategoryIDQuery | LoadByCategoryNameQuery


async def handle(*, db_session: AsyncSession, query: LoadCategoryQuery, **_) -> Category | None:
    return await db_session.scalar(apply_queries(select(Category), query))


@auto_parse_kwargs(query_type=LoadCategoryQuery)
async def auto_handle(**kwargs: Any) -> Category | None:
    return await handle(**kwargs)
