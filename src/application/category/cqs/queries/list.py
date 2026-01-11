from typing import Literal

from sqlalchemy import ColumnElement, not_

from application.category.cqs.queries.load import CategoryIsolateByUser
from application.category.schemas.model import (
    SchemaCategoryCode,
    SchemaCategoryID,
    SchemaCategoryParentID,
    SchemaCategoryStatus,
    SchemaCategoryTags,
)
from application.user.schemas.model import SchemaUserID
from domain.category.model import Category
from shared.cqs.generator import generate_list_handle
from shared.cqs.query import QueryFilterBase


class CategoryStatusQuery(QueryFilterBase):
    status: SchemaCategoryStatus | list[SchemaCategoryStatus]

    def render_filter(self) -> ColumnElement[bool]:
        if isinstance(self.status, list):
            return Category.status.in_(self.status)
        return Category.status == self.status


class CategoryCodeQuery(QueryFilterBase):
    code: SchemaCategoryCode | list[SchemaCategoryCode]

    def render_filter(self) -> ColumnElement[bool]:
        if isinstance(self.code, list):
            return Category.code.in_(self.code)
        return Category.code == self.code


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
    parent_id: None | SchemaCategoryParentID | list[SchemaCategoryParentID]

    def render_filter(self) -> ColumnElement[bool]:
        if self.parent_id is None:
            return Category.parent_id.is_(None)
        if isinstance(self.parent_id, list):
            return Category.parent_id.in_(self.parent_id)
        return Category.parent_id == self.parent_id


class CategoryTagsQuery(QueryFilterBase):
    tags: SchemaCategoryTags
    filter_type: Literal['HAVE_ANY', 'HAVE_ALL', 'HAVE_NOTHING', 'HAVE_EXACTLY'] = 'HAVE_ALL'

    def render_filter(self) -> ColumnElement[bool]:
        match self.filter_type:
            case 'HAVE_ALL':
                return Category.tags.contains(self.tags)
            case 'HAVE_ANY':
                return Category.tags.overlap(self.tags)
            case 'HAVE_NOTHING':
                return not_(Category.tags.overlap(self.tags))
            case 'HAVE_EXACTLY':
                return Category.tags == self.tags

        raise ValueError(f'Unknown filter_type={self.filter_type}')


handle = generate_list_handle(
    entity_cls=Category,
    query_types=[
        CategoryStatusQuery,
        CategoryTagsQuery,
        CategoryIDQuery,
        CategoryCodeQuery,
        CategoryUserIDQuery,
        CategoryParentIDQuery,
        CategoryIsolateByUser,  # Изолируем по пользователю если пробросили cur_user
    ],
)
