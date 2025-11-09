from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import ColumnElement, select
from domain.user.model import User
from shared.cqs.parser import auto_parse_kwargs
from shared.cqs.query import QueryFilterBase, apply_queries
from application.user.schemas.model import SchemaUserID, SchemaUserName


class LoadByUserNameQuery(QueryFilterBase):
    name: SchemaUserName

    def render_filter(self) -> ColumnElement[bool]:
        return User.name == self.name


class LoadUserByIDQuery(QueryFilterBase):
    id: SchemaUserID

    def render_filter(self) -> ColumnElement[bool]:
        return User.id == self.id


LoadUserQuery = LoadByUserNameQuery | LoadUserByIDQuery


async def handle(*, db_session: AsyncSession, query: LoadUserQuery | None = None, **_) -> User | None:
    if not query:
        raise ValueError('Query must not be None')

    return await db_session.scalar(apply_queries(select(User), query))


@auto_parse_kwargs(query_type=LoadUserQuery)
async def auto_handle(**kwargs: Any) -> User | None:
    return await handle(**kwargs)
