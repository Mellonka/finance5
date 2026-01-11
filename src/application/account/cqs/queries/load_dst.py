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


class LoadByDestinationAccountIDQuery(QueryFilterBase):
    dst_account_id: SchemaAccountID

    def render_filter(self) -> ColumnElement[bool]:
        return Account.id == self.dst_account_id


class LoadByDestinationAccountCOdeQuery(QueryFilterBase):
    dst_account_code: SchemaAccountCode

    def render_filter(self) -> ColumnElement[bool]:
        return Account.code == self.dst_account_code


load_dst_account = generate_load_handle(
    base_statement=select(Account),
    query_types=[
        LoadByDestinationAccountIDQuery | LoadByDestinationAccountCOdeQuery,
        LoadAccountForUpdate,
        AccountsIsolateByUser,  # Изолируем по пользователю если пробросили cur_user
    ],
)
load_dst_account = generate_load_decorator(
    load_dst_account, 'dst_account', AccountNotFoundError('Destination account not found error')
)
