import random
from dataclasses import dataclass
from typing import Any, Callable
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from application.account.cqs.commands.create import auto_handle as account_create_handle
from application.account.cqs.queries.load import auto_handle as account_load_handle
from application.user.cqs.commands.create import auto_handle as user_create_handle
from application.user.cqs.queries.load import auto_handle as user_load_handle
from domain.account.model import Account, EnumAccountType
from domain.user.model import User
from domain.vo.money import Money


@dataclass(slots=True)
class Dataset:
    uuid: Callable[[], str]
    uuid7: Callable[[], UUID]
    session_maker: async_sessionmaker[AsyncSession]

    async def user(self, **kwargs: Any) -> User:
        kwargs.setdefault('name', self.uuid())
        kwargs.setdefault('description', random.choice([None, self.uuid()]))
        kwargs.setdefault('tags', [self.uuid() for _ in range(random.randint(0, 5))])

        async with self.session_maker() as db_session:
            return await user_create_handle(db_session=db_session, **kwargs)

    async def load_user(self, **kwargs: Any) -> User | None:
        async with self.session_maker() as db_session:
            return await user_load_handle(db_session=db_session, **kwargs)

    async def account(self, **kwargs: Any) -> Account:
        kwargs.setdefault('name', self.uuid())
        kwargs.setdefault('description', random.choice([None, self.uuid()]))
        kwargs.setdefault('balance', Money(random.randint(0, 1_000_000) + random.random()))
        kwargs.setdefault('currency', 'RUB')
        kwargs.setdefault('type', EnumAccountType.MONEY)
        kwargs.setdefault('tags', [self.uuid() for _ in range(random.randint(0, 5))])

        if user := kwargs.pop('user', None):
            kwargs['user_id'] = user.id
        elif user_id := kwargs.pop('user_id', None):
            user = await self.load_user(user_id=user_id)
        else:
            user = await self.user()
            kwargs['user_id'] = user.id

        async with self.session_maker() as db_session:
            return await account_create_handle(db_session=db_session, cur_user=user, **kwargs)

    async def load_account(self, **kwargs: Any) -> Account | None:
        async with self.session_maker() as db_session:
            return await account_load_handle(db_session=db_session, **kwargs)
