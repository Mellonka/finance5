import datetime as dt
from typing import Literal, get_args

from sqlalchemy import ColumnElement, Select, not_, select, true
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
from domain.user.model import User
from shared.cqs.query import QueryFilterBase, QueryStatementBase, apply_queries, parse_query_kwargs


class TransactionDateRangeQuery(QueryFilterBase):
    min_date: dt.date | None
    max_date: dt.date | None

    def render_filter(self) -> ColumnElement[bool]:
        if self.min_date and self.max_date:
            return Transaction.date.between(self.min_date, self.max_date)
        elif self.min_date:
            return Transaction.date >= self.min_date
        elif self.max_date:
            return Transaction.date <= self.max_date
        return true()


class TransactionAmountQuery(QueryFilterBase):
    min_amount: dt.date | None
    max_amount: dt.date | None

    def render_filter(self) -> ColumnElement[bool]:
        if self.min_amount and self.max_amount:
            return Transaction.amount.between(self.min_amount, self.max_amount)
        elif self.min_amount:
            return Transaction.amount >= self.min_amount
        elif self.max_amount:
            return Transaction.amount <= self.max_amount
        return true()


class TransactionTagsQuery(QueryFilterBase):
    tags: list[str]
    filter_type: Literal['HAVE_ANY', 'HAVE_ALL', 'HAVE_NOTHING', 'HAVE_SAME'] = 'HAVE_ALL'

    def render_filter(self) -> ColumnElement[bool]:
        match self.filter_type:
            case 'HAVE_ALL':
                return Transaction.tags.contains(self.tags)
            case 'HAVE_ANY':
                return Transaction.tags.overlap(self.tags)
            case 'HAVE_NOTHING':
                return not_(Transaction.tags.overlap(self.tags))
            case 'HAVE_SAME':
                return Transaction.tags == self.tags

        raise ValueError(f'Unknown filter_type={self.filter_type}')


class TransactionTypeQuery(QueryFilterBase):
    type: SchemaTransactionType | list[SchemaTransactionType]

    def render_filter(self) -> ColumnElement[bool]:
        if isinstance(self.type, list):
            return Transaction.type.in_(self.type)
        return Transaction.type == self.type


class TransactionStatusQuery(QueryFilterBase):
    status: SchemaTransactionStatus | list[SchemaTransactionStatus]

    def render_filter(self) -> ColumnElement[bool]:
        if isinstance(self.status, list):
            return Transaction.status.in_(self.status)
        return Transaction.status == self.status


class TransactionAccountNameQuery(QueryFilterBase):
    account_name: SchemaAccountName | list[SchemaAccountName]

    def process_statement(self, statement: Select) -> Select:
        return statement.join(Account, Transaction.account_id == Account.id).where(
            Account.code.in_(self.account_name)
            if isinstance(self.account_name, list)
            else Account.code == self.account_name
        )


class TransactionCategoryNameQuery(QueryStatementBase):
    category_name: SchemaCategoryName | list[SchemaCategoryName]

    def process_statement(self, statement: Select) -> Select:
        return statement.join(Category, Transaction.category_id == Category.id).where(
            Category.name.in_(self.category_name)
            if isinstance(self.category_name, list)
            else Category.name == self.category_name
        )


class TransactionIDQuery(QueryFilterBase):
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


class TransactionCursorQuery(QueryFilterBase):
    cursor: str

    def render_filter(self) -> ColumnElement[bool]:
        return super().render_filter()


ListTransactionQuery = (
    TransactionDateRangeQuery
    | TransactionAmountQuery
    | TransactionTagsQuery
    | TransactionTypeQuery
    | TransactionStatusQuery
    | TransactionAccountNameQuery
    | TransactionCategoryNameQuery
    | TransactionIDQuery
    | TransactionAccountIDQuery
    | TransactionCategoryIDQuery
)
list_transaction_query_types = get_args(ListTransactionQuery)


async def handle(
    *,
    cur_user: User,
    db_session: AsyncSession,
    queries: list[ListTransactionQuery] | None = None,
    **kwargs,
) -> list[Transaction]:
    statement = apply_queries(
        select(Transaction),
        *(queries or []),
        *parse_query_kwargs(kwargs, list_transaction_query_types),
    )
    return list(await db_session.scalars(statement.where(Transaction.user_id == cur_user.id)))
