from sqlalchemy import ColumnElement, Select, and_, select

from application.account.cqs.queries.load import AccountsIsolateByUser
from application.account.schemas.model import SchemaAccountCode, SchemaAccountID
from application.account.storage.repository import AccountEventRepository
from domain.account.events import AccountEvent
from domain.account.model import Account
from shared.cqs.generator import generate_list_handle_with_cursor
from shared.cqs.query import QueryFilterBase, QueryStatementBase


class EventsIsolateByAccountID(QueryFilterBase):
    account_id: SchemaAccountID

    def render_filter(self) -> ColumnElement[bool]:
        return AccountEvent.account_id == self.account_id


class EventsIsolateByAccountCode(QueryStatementBase):
    code: SchemaAccountCode

    def apply_query(self, statement: Select) -> Select:
        return statement.join(Account, and_(Account.id == AccountEvent.account_id, Account.code == self.code))


EventsIsolateByAccount = EventsIsolateByAccountID | EventsIsolateByAccountCode


handle = generate_list_handle_with_cursor(
    base_statement=select(AccountEvent).order_by(AccountEvent.serial.desc()),
    query_types=[
        EventsIsolateByAccount,  # Изолируем по аккаунту если пробросили айдишник
        AccountsIsolateByUser,  # Изолируем по пользователю если пробросили cur_user
    ],
    entity_repository_cls=AccountEventRepository,
)
