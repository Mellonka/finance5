from typing import Literal

from sqlalchemy import ColumnElement, not_, select

from application.account.cqs.queries.load import AccountsIsolateByUser
from application.account.schemas.model import (
    SchemaAccountCode,
    SchemaAccountID,
    SchemaAccountTags,
    SchemaAccountType,
)
from application.user.schemas.model import SchemaUserID
from domain.account.model import Account, EnumAccountStatus
from shared.cqs.generator import generate_list_handle
from shared.cqs.query import QueryFilterBase


class AccountTypeQuery(QueryFilterBase):
    type: SchemaAccountType | list[SchemaAccountType]

    def render_filter(self) -> ColumnElement[bool]:
        if isinstance(self.type, list):
            return Account.type.in_(self.type)
        return Account.type == self.type


class AccountCodeQuery(QueryFilterBase):
    code: SchemaAccountCode | list[SchemaAccountCode]

    def render_filter(self) -> ColumnElement[bool]:
        if isinstance(self.code, list):
            return Account.code.in_(self.code)
        return Account.code == self.code


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


class AccountTagsQuery(QueryFilterBase):
    tags: SchemaAccountTags
    filter_type: Literal['HAVE_ANY', 'HAVE_ALL', 'HAVE_NOTHING', 'HAVE_EXACTLY'] = 'HAVE_ALL'

    def render_filter(self) -> ColumnElement[bool]:
        match self.filter_type:
            case 'HAVE_ALL':
                return Account.tags.contains(self.tags)
            case 'HAVE_ANY':
                return Account.tags.overlap(self.tags)
            case 'HAVE_NOTHING':
                return not_(Account.tags.overlap(self.tags))
            case 'HAVE_EXACTLY':
                return Account.tags == self.tags

        raise ValueError(f'Unknown filter_type={self.filter_type}')


handle = generate_list_handle(
    base_statement=select(Account).where(Account.status == EnumAccountStatus.ACTIVE).order_by(Account.id),
    query_types=[
        AccountTypeQuery,
        AccountTagsQuery,
        AccountIDQuery,
        AccountCodeQuery,
        AccountUserIDQuery,
        AccountsIsolateByUser,  # Изолируем по пользователю если пробросили cur_user
    ],
)
