from sqlalchemy import ColumnElement, Select, select

from application.account.errors import AccountNotFoundError
from application.account.schemas.model import SchemaAccountCode, SchemaAccountID
from domain.account.model import Account
from domain.user.model import User
from shared.cqs.generator import generate_load_decorator, generate_load_handle
from shared.cqs.query import QueryFilterBase, QueryStatementBase


class LoadByAccountIDQuery(QueryFilterBase):
    account_id: SchemaAccountID

    def render_filter(self) -> ColumnElement[bool]:
        return Account.id == self.account_id


class LoadByAccountCodeQuery(QueryFilterBase):
    code: SchemaAccountCode

    def render_filter(self) -> ColumnElement[bool]:
        return Account.code == self.code


class AccountsIsolateByUser(QueryFilterBase):
    cur_user: User

    def render_filter(self) -> ColumnElement[bool]:
        return Account.user_id == self.cur_user.id


class LoadAccountForUpdate(QueryStatementBase):
    for_update: bool

    def apply_query(self, statement: Select) -> Select:
        if self.for_update:
            return statement.with_for_update()
        return statement


handle = generate_load_handle(
    base_statement=select(Account),
    query_types=[
        LoadByAccountIDQuery | LoadByAccountCodeQuery,
        LoadAccountForUpdate,
        AccountsIsolateByUser,  # Изолируем по пользователю если пробросили cur_user
    ],
)
load_account = generate_load_decorator(handle, 'account', AccountNotFoundError('Account not found'))
