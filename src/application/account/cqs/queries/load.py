from pydantic import TypeAdapter
from sqlalchemy import ColumnElement
from sqlalchemy.ext.asyncio import AsyncSession

from application.account.schemas.model import SchemaAccountID, SchemaAccountName
from domain.account.model import Account
from shared.cqs.query import QueryFilterBase, QueryHandlerABC


class LoadByAccountIDQuery(QueryFilterBase):
    account_id: SchemaAccountID

    def render_filter(self) -> ColumnElement[bool]:
        return Account.id == self.account_id


class LoadByAccountNameQuery(QueryFilterBase):
    name: SchemaAccountName

    def render_filter(self) -> ColumnElement[bool]:
        return Account.name == self.name


type LoadAccountQuery = QueryFilterBase | LoadByAccountIDQuery | LoadByAccountNameQuery
load_query_parse = TypeAdapter(LoadAccountQuery).validate_python


class AccountLoadHandler(QueryHandlerABC):
    async def handle(
        self, *, db_session: AsyncSession, query: LoadAccountQuery | None = None, **kwargs
    ) -> Account | None:
        return await self.load(db_session=db_session, query=query, **kwargs)


handler = AccountLoadHandler(Account, load_query_parse)
