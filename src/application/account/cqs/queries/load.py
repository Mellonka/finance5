from typing import Any, Callable

from pydantic import TypeAdapter
from sqlalchemy import ColumnElement, and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from application.account.schemas.model import SchemaAccountID, SchemaAccountName
from domain.account.model import Account
from domain.user.model import UserID
from shared.cqs.base import QueryBase


class LoadAccountQueryBase(QueryBase):
    def render_filter(self) -> ColumnElement[bool]:
        raise NotImplementedError


class LoadByAccountIDQuery(LoadAccountQueryBase):
    account_id: SchemaAccountID

    def render_filter(self) -> ColumnElement[bool]:
        return Account.id == self.account_id


class LoadByManyAccountIDQuery(LoadAccountQueryBase):
    account_id: list[SchemaAccountID]

    def render_filter(self) -> ColumnElement[bool]:
        return Account.id.in_(self.account_id)


class LoadByAccountNameAndUserIDQuery(LoadAccountQueryBase):
    user_id: UserID
    name: SchemaAccountName

    def render_filter(self) -> ColumnElement[bool]:
        return and_(Account.name == self.name, Account.user_id == self.user_id)


type LoadAccountQuery = LoadByAccountIDQuery | LoadByAccountNameAndUserIDQuery | LoadAccountQueryBase
query_parser: Callable[[dict[str, Any]], LoadAccountQuery] = TypeAdapter(LoadAccountQuery).validate_python


async def handle(*, db_session: AsyncSession, query: LoadAccountQuery | None = None, **kwargs) -> Account | None:
    if query is None:
        query = query_parser(kwargs)

    if type(query) is LoadAccountQueryBase:
        return None

    return await db_session.scalar(select(Account).where(query.render_filter()))
