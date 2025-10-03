from enum import StrEnum, auto

from pydantic import Field
from sqlalchemy import ColumnElement, and_, select, true
from sqlalchemy.ext.asyncio import AsyncSession

from application.account.cqs.schemas.model import (
    SchemaAccountStatus,
    SchemaAccountTags,
    SchemaAccountType,
)
from domain.account.model import Account, AccountID
from shared.cqs.base import QueryBase

DEFAULT_LIMIT: int = 100


class ListAccountQueryBase(QueryBase):
    def render_filter(self) -> ColumnElement[bool]:
        raise NotImplementedError


class ListAccountAlwaysTrueQuery(ListAccountQueryBase):
    def render_filter(self) -> ColumnElement[bool]:
        return true()


class ListAccountTypeAndStatusQuery(ListAccountQueryBase):
    type: list[SchemaAccountType] = Field(default_factory=list)
    status: list[SchemaAccountStatus] = Field(default_factory=list)

    def render_filter(self) -> ColumnElement[bool]:
        type_filter = Account.type.in_(self.type) if self.type else true()
        status_filter = Account.status.in_(self.status) if self.status else true()

        return and_(type_filter, status_filter)


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


type ListAccountQuery = ListAccountAlwaysTrueQuery | ListAccountTypeAndStatusQuery | ListAccountTagsQuery


async def handle(
    *,
    queries: list[ListAccountQuery],
    db_session: AsyncSession,
    cursor: AccountID | None = None,
    limit: int,
    **_,
) -> list[Account]:
    if not queries:
        queries = [ListAccountAlwaysTrueQuery()]

    return list(
        await db_session.scalars(
            select(Account)
            .where(Account.id < cursor if cursor is not None else true())
            .where(*(q.render_filter() for q in queries))
            .order_by(Account.id.desc())
            .limit(limit)
        )
    )
