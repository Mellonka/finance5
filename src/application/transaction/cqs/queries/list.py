from pydantic import TypeAdapter
from sqlalchemy import ColumnElement, Select
from sqlalchemy.ext.asyncio import AsyncSession

from application.account.schemas.model import SchemaAccountID, SchemaAccountName
from application.category.schemas.model import SchemaCategoryID, SchemaCategoryName
from application.transaction.schemas.model import (
    SchemaTransactionID,
    SchemaTransactionStatus,
    SchemaTransactionType,
)
from domain.account.model import Account
from domain.category.model import Category
from domain.transaction.model import Transaction
from shared.cqs.query import (
    QueryFilterBase,
    DateRangeQueryBase,
    MoneyRangeQueryBase,
    TagsQueryBase,
    StatusQueryBase,
    TypeQueryBase,
    QueryStatementBase,
    QueryHandlerABC,
)
from application.transaction.cqs.queries.load import load_query_parse


class TransactionDateRangeQuery(DateRangeQueryBase, entity_attr=Transaction.date):
    pass


class TransactionAmountQuery(MoneyRangeQueryBase, entity_attr=Transaction.amount):
    pass


class TransactionTagsQuery(TagsQueryBase, entity_attr=Transaction.tags):
    pass


class TransactionTypeQuery(TypeQueryBase[SchemaTransactionType], entity_attr=Transaction.type):
    pass


class TransactionStatusQuery(StatusQueryBase[SchemaTransactionStatus], entity_attr=Transaction.status):
    pass


class TransactionAccountNameQuery(QueryStatementBase[Transaction]):
    account_name: SchemaAccountName | list[SchemaAccountName]

    def process_statement(self, statement: Select[tuple[Transaction]]) -> Select[tuple[Transaction]]:
        return statement.join(Account, Transaction.account_id == Account.id).where(
            Account.name.in_(self.account_name)
            if isinstance(self.account_name, list)
            else Account.name == self.account_name
        )


class TransactionCategoryNameQuery(QueryStatementBase[Transaction]):
    category_name: SchemaCategoryName | list[SchemaCategoryName]

    def process_statement(self, statement: Select[tuple[Transaction]]) -> Select[tuple[Transaction]]:
        return statement.join(Category, Transaction.category_id == Category.id).where(
            Category.name.in_(self.category_name)
            if isinstance(self.category_name, list)
            else Category.name == self.category_name
        )


class TransactionManyIDQuery(QueryFilterBase):
    transaction_id: SchemaTransactionID | list[SchemaTransactionID]

    def render_filter(self) -> ColumnElement[bool]:
        if isinstance(self.transaction_id, list):
            return Transaction.id.in_(self.transaction_id)
        return Transaction.id == self.transaction_id


class TransactionAccountIDQuery(QueryFilterBase):
    account_id: SchemaAccountID | list[SchemaAccountID]

    def render_filter(self) -> ColumnElement[bool]:
        if isinstance(self.account_id, list):
            return Transaction.account_id.in_(self.account_id)
        return Transaction.account_id == self.account_id


class TransactionCategoryIDQuery(QueryFilterBase):
    category_id: SchemaCategoryID | list[SchemaCategoryID]

    def render_filter(self) -> ColumnElement[bool]:
        if isinstance(self.category_id, list):
            return Transaction.category_id.in_(self.category_id)
        return Transaction.category_id == self.category_id


type ListTransactionQuery = (
    TransactionDateRangeQuery
    | TransactionAmountQuery
    | TransactionTagsQuery
    | TransactionTypeQuery
    | TransactionStatusQuery
    | TransactionAccountNameQuery
    | TransactionCategoryNameQuery
    | TransactionManyIDQuery
    | TransactionAccountIDQuery
    | TransactionCategoryIDQuery
)
list_queries_parse = TypeAdapter(list[ListTransactionQuery]).validate_python


class TransactionListHandler(QueryHandlerABC):
    async def handle(self, *, db_session: AsyncSession, queries: list[ListTransactionQuery], **_) -> list[Transaction]:
        return await self.list(db_session=db_session, queries=queries)  # pyright: ignore[reportArgumentType]


handler = TransactionListHandler(Transaction, load_query_parse)
