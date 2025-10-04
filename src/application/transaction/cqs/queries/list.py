from enum import StrEnum, auto
import operator
import datetime as dt

from pydantic import Field, TypeAdapter
from sqlalchemy import ColumnElement, select
from sqlalchemy.ext.asyncio import AsyncSession

from application.account.schemas.model import SchemaAccountID
from application.category.schemas.model import SchemaCategoryID
from application.transaction.schemas.model import (
    SchemaTransactionAmount,
    SchemaTransactionTags,
    SchemaTransactionType,
)
from domain.transaction.model import Transaction, TransactionID
from domain.user.model import UserID
from shared.cqs.base import QueryBase


class ListTransactionQueryBase(QueryBase):
    def render_filter(self) -> ColumnElement[bool]:
        raise NotImplementedError


class ComparableFieldFilterType(StrEnum):
    LT = auto()
    LE = auto()
    EQ = auto()
    GE = auto()
    GT = auto()

    def operator(self, left, right) -> ColumnElement[bool]:
        return getattr(operator, self.value)(left, right)


class ListTransactionDateQuery(ListTransactionQueryBase):
    date: dt.date
    filter_type: ComparableFieldFilterType

    def render_filter(self) -> ColumnElement[bool]:
        return self.filter_type.operator(Transaction.date, self.date)


class TagsFilterType(StrEnum):
    ALL = auto()
    AT_LEAST_ONE = auto()


class ListTransactionTagsQuery(ListTransactionQueryBase):
    tags: SchemaTransactionTags = Field(default_factory=list)
    filter_type: TagsFilterType = TagsFilterType.ALL

    def render_filter(self) -> ColumnElement[bool]:
        match self.filter_type:
            case TagsFilterType.ALL:
                return Transaction.tags.contained_by(self.tags)
            case TagsFilterType.AT_LEAST_ONE:
                return Transaction.tags.overlap(self.tags)

        raise NotImplementedError


class ListTransactionTypeQuery(ListTransactionQueryBase):
    type: SchemaTransactionType

    def render_filter(self) -> ColumnElement[bool]:
        return Transaction.type == self.type


class ListTransactionAccountQuery(ListTransactionQueryBase):
    account_id: list[SchemaAccountID] = Field(default_factory=list)

    def render_filter(self) -> ColumnElement[bool]:
        if isinstance(self.account_id, list):
            return Transaction.account_id.in_(self.account_id)
        return Transaction.account_id == self.account_id


class ListTransactionCategoryQuery(ListTransactionQueryBase):
    category_id: list[SchemaCategoryID] = Field(default_factory=list)

    def render_filter(self) -> ColumnElement[bool]:
        if isinstance(self.category_id, list):
            return Transaction.category_id.in_(self.category_id)
        return Transaction.category_id == self.category_id


class ListTransactionAmountQuery(ListTransactionQueryBase):
    amount: SchemaTransactionAmount
    filter_type: ComparableFieldFilterType

    def render_filter(self) -> ColumnElement[bool]:
        return self.filter_type.operator(Transaction.amount, self.amount)


type ListTransactionQuery = (
    ListTransactionDateQuery
    | ListTransactionTagsQuery
    | ListTransactionTypeQuery
    | ListTransactionAccountQuery
    | ListTransactionCategoryQuery
    | ListTransactionAmountQuery
)
query_parser = TypeAdapter(ListTransactionQuery).validate_python


async def handle(
    *,
    user_id: UserID,
    queries: list[ListTransactionQuery],
    db_session: AsyncSession,
    cursor: TransactionID | None = None,
    limit: int | None = None,
    **_,
) -> list[Transaction]:
    statement = select(Transaction).where(Transaction.user_id == user_id).order_by(Transaction.id.desc())

    if cursor:
        statement = statement.where(Transaction.id < cursor)
    if limit is not None:
        statement = statement.limit(limit)
    if queries:
        statement = statement.where(*(q.render_filter() for q in queries))

    return list(await db_session.scalars(statement))
