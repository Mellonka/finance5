from typing import Any, Callable

from pydantic import TypeAdapter
from sqlalchemy import ColumnElement, select
from sqlalchemy.ext.asyncio import AsyncSession

from application.transaction.schemas.model import SchemaTransactionID
from domain.transaction.model import Transaction
from shared.cqs.base import QueryBase


class LoadTransactionQueryBase(QueryBase):
    def render_filter(self) -> ColumnElement[bool]:
        raise NotImplementedError


class LoadByTransactionIDQuery(LoadTransactionQueryBase):
    transaction_id: SchemaTransactionID

    def render_filter(self) -> ColumnElement[bool]:
        return Transaction.id == self.transaction_id


class LoadByManyTransactionIDQuery(LoadTransactionQueryBase):
    transaction_id: list[SchemaTransactionID]

    def render_filter(self) -> ColumnElement[bool]:
        return Transaction.id.in_(self.transaction_id)


type LoadTransactionQuery = LoadByTransactionIDQuery | LoadTransactionQueryBase
query_parser: Callable[[dict[str, Any]], LoadTransactionQuery] = TypeAdapter(LoadTransactionQuery).validate_python


async def handle(
    *, db_session: AsyncSession, query: LoadTransactionQuery | None = None, **kwargs
) -> Transaction | None:
    if query is None:
        query = query_parser(kwargs)

    if type(query) is LoadTransactionQueryBase:
        return None

    return await db_session.scalar(select(Transaction).where(query.render_filter()))
