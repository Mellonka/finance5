from pydantic import TypeAdapter
from sqlalchemy import ColumnElement
from sqlalchemy.ext.asyncio import AsyncSession

from application.category.schemas.model import (
    SchemaCategoryID,
    SchemaCategoryName,
    SchemaCategoryParentID,
    SchemaCategoryStatus,
)
from domain.category.model import Category
from shared.cqs.query import StatusQueryBase, TagsQueryBase, QueryFilterBase, NameQueryBase

from application.category.cqs.queries.load import load_query_parse
from shared.cqs.query.handler import QueryHandlerABC


class CategoryStatusQuery(StatusQueryBase[SchemaCategoryStatus], entity_attr=Category.status):
    pass


class CategoryTagsQuery(TagsQueryBase, entity_attr=Category.tags):
    pass


class CategoryManyNameQuery(NameQueryBase[SchemaCategoryName], entity_attr=Category.name):
    pass


class CategoryManyIDQuery(QueryFilterBase):
    category_id: SchemaCategoryID | list[SchemaCategoryID]

    def render_filter(self) -> ColumnElement[bool]:
        if isinstance(self.category_id, list):
            return Category.id.in_(self.category_id)
        return Category.id == self.category_id


class CategoryParentIDQuery(QueryFilterBase):
    parent_id: SchemaCategoryParentID

    def render_filter(self) -> ColumnElement[bool]:
        return Category.parent_id == self.parent_id


type ListCategoryQuery = (
    CategoryStatusQuery | CategoryTagsQuery | CategoryManyIDQuery | CategoryManyNameQuery | CategoryParentIDQuery
)
list_query_parse = TypeAdapter(ListCategoryQuery).validate_python


class CategoryListHandler(QueryHandlerABC):
    async def handle(self, *, db_session: AsyncSession, queries: list[ListCategoryQuery], **_) -> list[Category]:
        return await self.list(db_session=db_session, queries=queries)  # pyright: ignore[reportArgumentType]


handler = CategoryListHandler(Category, load_query_parse)
