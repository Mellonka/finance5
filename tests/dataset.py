import random
from dataclasses import dataclass
from typing import Callable
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from application.account.cqs.commands.create import CreateAccountCommand
from application.account.cqs.commands.create import handle as create_handle
from application.account.cqs.queries.load import handle as load_handle
from domain.account.model import Account, EnumAccountType
from domain.vo.currency import Currency
from domain.vo.money import Money


@dataclass(slots=True)
class Dataset:
    uuid: Callable[[], str]
    uuid7: Callable[[], UUID]
    session_maker: async_sessionmaker[AsyncSession]

    async def account(self, **kwargs) -> Account:
        kwargs.setdefault('name', self.uuid())
        kwargs.setdefault('description', random.choice([None, self.uuid()]))
        kwargs.setdefault('balance', Money(random.randint(0, 1_000_000) + random.random()))
        kwargs.setdefault('currency', Currency('RUB'))
        kwargs.setdefault('type', EnumAccountType.MONEY)
        kwargs.setdefault('tags', [self.uuid() for _ in range(random.randint(0, 5))])
        kwargs.setdefault('user_id', self.uuid7())

        async with self.session_maker() as db_session:
            return await create_handle(db_session=db_session, command=CreateAccountCommand(**kwargs))

    async def load_account(self, db_session: AsyncSession | None = None, **kwargs) -> Account | None:
        async with self.session_maker() as db_session:
            return await load_handle(db_session=db_session, **kwargs)
