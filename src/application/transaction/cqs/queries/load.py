from pydantic import TypeAdapter
from sqlalchemy import ColumnElement
from sqlalchemy.ext.asyncio import AsyncSession

from application.transaction.schemas.model import SchemaTransactionID
from domain.transaction.model import Transaction
from shared.cqs.query import QueryFilterBase
from shared.cqs.query.handler import QueryHandlerABC


class TransactionIDQuery(QueryFilterBase):
    transaction_id: SchemaTransactionID

    def render_filter(self) -> ColumnElement[bool]:
        return Transaction.id == self.transaction_id


type LoadTransactionQuery = QueryFilterBase | TransactionIDQuery
load_query_parse = TypeAdapter(LoadTransactionQuery).validate_python


class TransactionLoadHandler(QueryHandlerABC):
    async def handle(
        self, *, db_session: AsyncSession, query: LoadTransactionQuery | None = None, **kwargs
    ) -> Transaction | None:
        return await self.load(db_session=db_session, query=query, **kwargs)


handler = TransactionLoadHandler(Transaction, load_query_parse)
