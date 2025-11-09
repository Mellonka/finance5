from sqlalchemy import ColumnElement, select
from sqlalchemy.ext.asyncio import AsyncSession

from application.transaction.schemas.model import SchemaTransactionID
from domain.transaction.model import Transaction
from domain.user.model import User
from shared.cqs.query import QueryFilterBase, apply_queries, parse_query_kwargs


class LoadByTransactionIDQuery(QueryFilterBase):
    transaction_id: SchemaTransactionID

    def render_filter(self) -> ColumnElement[bool]:
        return Transaction.id == self.transaction_id


async def handle(
    *, cur_user: User, db_session: AsyncSession, query: LoadByTransactionIDQuery | None = None, **kwargs
) -> Transaction | None:
    if not query:
        queries = parse_query_kwargs(kwargs, [LoadByTransactionIDQuery])
        if len(queries) == 1:
            query = queries[0]  # type: ignore

    if not query:
        return None

    statement = apply_queries(select(Transaction), query)
    return await db_session.scalar(statement.where(Transaction.user_id == cur_user.id))
