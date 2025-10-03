from typing import Any, Callable

from pydantic import TypeAdapter
from sqlalchemy import ColumnElement, select
from sqlalchemy.ext.asyncio import AsyncSession

from application.account.cqs.schemas.model import SchemaAccountID, SchemaAccountName
from domain.account.model import Account
from shared.cqs.base import QueryBase
from shared.cqs.middlewares.inject_entity import InjectEntityDecorator


class LoadAccountQueryBase(QueryBase):
    def render_filter(self) -> ColumnElement[bool]:
        raise NotImplementedError


class LoadByAccountIDQuery(LoadAccountQueryBase):
    account_id: SchemaAccountID

    def render_filter(self) -> ColumnElement[bool]:
        return Account.id == self.account_id


class LoadByAccountNameQuery(LoadAccountQueryBase):
    name: SchemaAccountName

    def render_filter(self) -> ColumnElement[bool]:
        return Account.name == self.name


type LoadAccountQuery = LoadByAccountIDQuery | LoadByAccountNameQuery | LoadAccountQueryBase
query_parser: Callable[[dict[str, Any]], LoadAccountQuery] = TypeAdapter(LoadAccountQuery).validate_python


async def handle(*, db_session: AsyncSession, query: LoadAccountQuery | None = None, **kwargs) -> Account | None:
    if query is None:
        query = query_parser(kwargs)

    if type(query) is LoadAccountQueryBase:
        return None

    return await db_session.scalar(select(Account).where(query.render_filter()))


class InjectAccountDecorator(InjectEntityDecorator):
    async def load_entity(self, *args, **kwargs) -> dict[str, Any]:
        return {'account': await handle(**kwargs)}


inject_entity = InjectAccountDecorator()
