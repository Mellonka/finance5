from pydantic import TypeAdapter
from sqlalchemy import ColumnElement
from sqlalchemy.ext.asyncio import AsyncSession

from application.account.schemas.model import (
    SchemaAccountID,
    SchemaAccountName,
    SchemaAccountStatus,
    SchemaAccountType,
)
from domain.account.model import Account
from shared.cqs.query import QueryFilterBase, TypeQueryBase, StatusQueryBase, TagsQueryBase, NameQueryBase
from application.account.cqs.queries.load import load_query_parse
from shared.cqs.query.handler import QueryHandlerABC


class AccountTypeQuery(TypeQueryBase[SchemaAccountType], entity_attr=Account.type):
    pass


class AccountStatusQuery(StatusQueryBase[SchemaAccountStatus], entity_attr=Account.status):
    pass


class AccountTagsQuery(TagsQueryBase, entity_attr=Account.tags):
    pass


class AccountManyNameQuery(NameQueryBase[SchemaAccountName], entity_attr=Account.name):
    pass


class AccountManyIDQuery(QueryFilterBase):
    account_id: SchemaAccountID | list[SchemaAccountID]

    def render_filter(self) -> ColumnElement[bool]:
        if isinstance(self.account_id, list):
            return Account.id.in_(self.account_id)
        return Account.id == self.account_id


type ListAccountQuery = (
    AccountTypeQuery | AccountStatusQuery | AccountTagsQuery | AccountManyIDQuery | AccountManyNameQuery
)
list_query_parse = TypeAdapter(ListAccountQuery).validate_python


class AccountListHandler(QueryHandlerABC):
    async def handle(self, *, db_session: AsyncSession, queries: list[ListAccountQuery], **_) -> list[Account]:
        return await self.list(db_session=db_session, queries=queries)  # pyright: ignore[reportArgumentType]


handler = AccountListHandler(Account, load_query_parse)
