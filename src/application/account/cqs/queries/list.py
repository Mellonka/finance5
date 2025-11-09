from typing import Any, Literal, get_args
from sqlalchemy import ColumnElement, not_, select
from sqlalchemy.ext.asyncio import AsyncSession

from application.account.schemas.model import (
    SchemaAccountID,
    SchemaAccountName,
    SchemaAccountStatus,
    SchemaAccountTags,
    SchemaAccountType,
)
from application.user.schemas.model import SchemaUserID
from domain.account.model import Account
from shared.cqs.parser import auto_parse_kwargs
from shared.cqs.query import QueryFilterBase, apply_queries


class AccountTypeQuery(QueryFilterBase):
    type: SchemaAccountType | list[SchemaAccountType]

    def render_filter(self) -> ColumnElement[bool]:
        if isinstance(self.type, list):
            return Account.type.in_(self.type)
        return Account.type == self.type


class AccountStatusQuery(QueryFilterBase):
    status: SchemaAccountStatus | list[SchemaAccountStatus]

    def render_filter(self) -> ColumnElement[bool]:
        if isinstance(self.status, list):
            return Account.status.in_(self.status)
        return Account.status == self.status


class AccountTagsQuery(QueryFilterBase):
    tags: SchemaAccountTags
    filter_type: Literal['HAVE_ANY', 'HAVE_ALL', 'HAVE_NOTHING', 'HAVE_SAME'] = 'HAVE_ALL'

    def render_filter(self) -> ColumnElement[bool]:
        match self.filter_type:
            case 'HAVE_ALL':
                return Account.tags.contains(self.tags)
            case 'HAVE_ANY':
                return Account.tags.overlap(self.tags)
            case 'HAVE_NOTHING':
                return not_(Account.tags.overlap(self.tags))
            case 'HAVE_SAME':
                return Account.tags == self.tags

        raise ValueError(f'Unknown filter_type={self.filter_type}')


class AccountNameQuery(QueryFilterBase):
    name: SchemaAccountName | list[SchemaAccountName]

    def render_filter(self) -> ColumnElement[bool]:
        if isinstance(self.name, list):
            return Account.code.in_(self.name)
        return Account.code == self.name


class AccountIDQuery(QueryFilterBase):
    account_id: SchemaAccountID | list[SchemaAccountID]

    def render_filter(self) -> ColumnElement[bool]:
        if isinstance(self.account_id, list):
            return Account.id.in_(self.account_id)
        return Account.id == self.account_id


class AccountUserIDQuery(QueryFilterBase):
    user_id: SchemaUserID | list[SchemaUserID]

    def render_filter(self) -> ColumnElement[bool]:
        if isinstance(self.user_id, list):
            return Account.user_id.in_(self.user_id)
        return Account.user_id == self.user_id


ListAccountQuery = (
    AccountTypeQuery | AccountStatusQuery | AccountTagsQuery | AccountIDQuery | AccountNameQuery | AccountUserIDQuery
)


async def handle(*, db_session: AsyncSession, queries: list[ListAccountQuery], **_) -> list[Account]:
    return list(await db_session.scalars(apply_queries(select(Account), *queries)))


@auto_parse_kwargs(query_types=get_args(ListAccountQuery))
async def auto_handle(**kwargs: Any) -> list[Account]:
    return await handle(**kwargs)
