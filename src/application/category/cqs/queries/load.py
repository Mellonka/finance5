from pydantic import TypeAdapter
from sqlalchemy import ColumnElement
from sqlalchemy.ext.asyncio import AsyncSession

from application.category.schemas.model import SchemaCategoryID, SchemaCategoryName
from domain.category.model import Category
from shared.cqs.query import QueryFilterBase, QueryHandlerABC


class LoadByCategoryIDQuery(QueryFilterBase):
    category_id: SchemaCategoryID

    def render_filter(self) -> ColumnElement[bool]:
        return Category.id == self.category_id


class LoadByCategoryNameQuery(QueryFilterBase):
    name: SchemaCategoryName

    def render_filter(self) -> ColumnElement[bool]:
        return Category.name == self.name


type LoadCategoryQuery = QueryFilterBase | LoadByCategoryIDQuery | LoadByCategoryNameQuery
load_query_parse = TypeAdapter(LoadCategoryQuery).validate_python


class CategoryLoadHandler(QueryHandlerABC):
    async def handle(
        self, *, db_session: AsyncSession, query: LoadCategoryQuery | None = None, **kwargs
    ) -> Category | None:
        return await self.load(db_session=db_session, query=query, **kwargs)


handler = CategoryLoadHandler(Category, load_query_parse)
