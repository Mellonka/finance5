from typing import Any
from sqlalchemy import ColumnElement, and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from application.account.schemas.model import SchemaAccountID, SchemaAccountName
from application.user.schemas.model import SchemaUserID
from domain.account.model import Account
from shared.cqs.parser import auto_parse_kwargs
from shared.cqs.query import QueryFilterBase, apply_queries


class LoadByAccountIDQuery(QueryFilterBase):
    account_id: SchemaAccountID

    def render_filter(self) -> ColumnElement[bool]:
        return Account.id == self.account_id


class LoadByAccountNameQuery(QueryFilterBase):
    name: SchemaAccountName
    user_id: SchemaUserID

    def render_filter(self) -> ColumnElement[bool]:
        return and_(Account.code == self.name, Account.user_id == self.user_id)


LoadAccountQuery = LoadByAccountIDQuery | LoadByAccountNameQuery


async def handle(*, db_session: AsyncSession, query: LoadAccountQuery, **_) -> Account | None:
    return await db_session.scalar(apply_queries(select(Account), query))


@auto_parse_kwargs(query_type=LoadAccountQuery)
async def auto_handle(**kwargs: Any) -> Account | None:
    return await handle(**kwargs)
