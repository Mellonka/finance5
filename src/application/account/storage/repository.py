import functools
from typing import ClassVar
from uuid import UUID

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.account.events import AccountEvent
from domain.account.model import Account
from shared.storage.filters import FilterHandler, UseInForArrays
from shared.storage.repository import RepositoryBase, RepositoryConfig


class AccountUseInForArrays(UseInForArrays[Account]):
    blacklist: ClassVar = {Account.tags}


class AccountFilterHandler(FilterHandler[Account]):
    @classmethod
    def account_id(
        cls, entity_cls: type[Account], statement: Select[tuple[Account]], value: list[UUID] | UUID
    ) -> Select[tuple[Account]]:
        if isinstance(value, list | tuple):
            return statement.where(Account.id.in_(value))
        return statement.where(Account.id == value)


class AccountRepository(
    RepositoryBase[Account],
    config=RepositoryConfig(
        entity_cls=Account,
        primary_key=Account.id,
        filter_handlers=[AccountUseInForArrays, AccountFilterHandler],
    ),
):
    pass


def provide_account_repo(func):
    @functools.wraps(func)
    async def wrapper(*, db_session: AsyncSession, **kwargs):
        if 'account_repo' not in kwargs:
            kwargs['account_repo'] = AccountRepository(db_session)
        return await func(db_session=db_session, **kwargs)

    return wrapper


class AccountEventRepository(
    RepositoryBase[AccountEvent],
    config=RepositoryConfig(
        entity_cls=AccountEvent,
        primary_key=AccountEvent.serial,
    ),
):
    pass


def provide_account_event_repo(func):
    @functools.wraps(func)
    async def wrapper(*, db_session: AsyncSession, **kwargs):
        if 'account_event_repo' not in kwargs:
            kwargs['account_event_repo'] = AccountEventRepository(db_session)
        return await func(db_session=db_session, **kwargs)

    return wrapper
