from sqlalchemy import ColumnElement, select

from application.account.cqs.queries.load import AccountsIsolateByUser, LoadAccountForUpdate
from application.account.errors import AccountNotFoundError
from application.account.schemas.model import (
    SchemaAccountCode,
    SchemaAccountID,
)
from domain.account.model import Account
from shared.cqs.generator import generate_load_decorator, generate_load_handle
from shared.cqs.query import QueryFilterBase


class LoadBySourceAccountIDQuery(QueryFilterBase):
    src_account_id: SchemaAccountID

    def render_filter(self) -> ColumnElement[bool]:
        return Account.id == self.src_account_id


class LoadBySourceAccountCodeQuery(QueryFilterBase):
    src_account_code: SchemaAccountCode

    def render_filter(self) -> ColumnElement[bool]:
        return Account.code == self.src_account_code


load_src_account = generate_load_handle(
    base_statement=select(Account),
    query_types=[
        LoadBySourceAccountIDQuery | LoadBySourceAccountCodeQuery,
        LoadAccountForUpdate,
        AccountsIsolateByUser,  # Изолируем по пользователю если пробросили cur_user
    ],
)
load_src_account = generate_load_decorator(
    load_src_account, 'src_account', AccountNotFoundError('Source account not found error')
)
