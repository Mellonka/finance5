import functools

from sqlalchemy import ColumnElement, Select, select

from application.category.schemas.model import SchemaCategoryCode, SchemaCategoryID
from domain.category.model import Category
from domain.user.model import User
from shared.cqs.generator import generate_load_handle
from shared.cqs.query import QueryFilterBase, QueryStatementBase


class LoadByCategoryIDQuery(QueryFilterBase):
    category_id: SchemaCategoryID

    def render_filter(self) -> ColumnElement[bool]:
        return Category.id == self.category_id


class LoadByCategoryCodeQuery(QueryFilterBase):
    code: SchemaCategoryCode

    def render_filter(self) -> ColumnElement[bool]:
        return Category.code == self.code


class CategoryIsolateByUser(QueryFilterBase):
    cur_user: User

    def render_filter(self) -> ColumnElement[bool]:
        return Category.user_id == self.cur_user.id


class LoadCategoryForUpdate(QueryStatementBase):
    for_update: bool

    def apply_query(self, statement: Select) -> Select:
        if self.for_update:
            return statement.with_for_update()
        return statement


handle = generate_load_handle(
    base_statement=select(Category),
    query_types=[
        LoadByCategoryIDQuery | LoadByCategoryCodeQuery,
        LoadCategoryForUpdate,
        CategoryIsolateByUser,  # Изолируем по пользователю если пробросили cur_user
    ],
)


def load_category(for_update: bool = False):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(**kwargs):
            kwargs['category'] = await handle(**kwargs, for_update=for_update)
            return await func(**kwargs)

        return wrapper

    return decorator
