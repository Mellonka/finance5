from enum import StrEnum, auto

from pydantic import Field
from sqlalchemy import ColumnElement, select, true
from sqlalchemy.ext.asyncio import AsyncSession

from application.account.schemas.model import (
    SchemaAccountStatus,
    SchemaAccountTags,
    SchemaAccountType,
)
from domain.account.model import Account, AccountID
from domain.user.model import UserID
from shared.cqs.base import QueryBase


class ListAccountQueryBase(QueryBase):
    def render_filter(self) -> ColumnElement[bool]:
        raise NotImplementedError


class ListAccountTypeQuery(ListAccountQueryBase):
    type: list[SchemaAccountType] = Field(default_factory=list)

    def render_filter(self) -> ColumnElement[bool]:
        return Account.type.in_(self.type) if self.type else true()


class ListAccountStatusQuery(ListAccountQueryBase):
    status: SchemaAccountStatus

    def render_filter(self) -> ColumnElement[bool]:
        return Account.status == self.status


class TagsFilterType(StrEnum):
    ALL = auto()
    AT_LEAST_ONE = auto()


class ListAccountTagsQuery(ListAccountQueryBase):
    tags: SchemaAccountTags = Field(default_factory=list)
    filter_type: TagsFilterType = TagsFilterType.ALL

    def render_filter(self) -> ColumnElement[bool]:
        match self.filter_type:
            case TagsFilterType.ALL:
                return Account.tags.contained_by(self.tags)
            case TagsFilterType.AT_LEAST_ONE:
                return Account.tags.overlap(self.tags)

        raise NotImplementedError


type ListAccountQuery = ListAccountTypeQuery | ListAccountStatusQuery | ListAccountTagsQuery


async def handle(
    *,
    user_id: UserID,
    db_session: AsyncSession,
    queries: list[ListAccountQuery] | None = None,
    cursor: AccountID | None = None,
    limit: int | None = None,
    **_,
) -> list[Account]:
    statement = select(Account).where(Account.user_id == user_id).order_by(Account.id.desc())

    if cursor:
        statement = statement.where(Account.id < cursor)
    if limit is not None:
        statement = statement.limit(limit)
    if queries:
        statement = statement.where(*(q.render_filter() for q in queries))

    return list(await db_session.scalars(statement))
