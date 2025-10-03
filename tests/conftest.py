from collections.abc import AsyncGenerator
from itertools import pairwise

import pytest
from dataset import Dataset
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from domain.account.model import Account
from shared.cqs.base import SchemaBase
from shared.utils import uuid as _uuid
from shared.utils import uuid7 as _uuid7


@pytest.fixture(scope='session')
def uuid7():
    return _uuid7


@pytest.fixture(scope='session')
def uuid():
    return _uuid


@pytest.fixture(scope='session')
def async_engine() -> AsyncEngine:
    return create_async_engine('sqlite+aiosqlite:///./temp/test.db', echo=False)


@pytest.fixture(scope='session')
def session_maker(async_engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)


@pytest.fixture(scope='session')
async def dataset(uuid, session_maker: async_sessionmaker[AsyncSession]) -> Dataset:
    return Dataset(uuid=uuid, session_maker=session_maker)


@pytest.fixture(scope='function')
async def db_session(session_maker: async_sessionmaker[AsyncSession]) -> AsyncGenerator[AsyncSession]:
    async with session_maker() as db_session:
        yield db_session


@pytest.fixture(autouse=True, scope='session')
async def create_test_tables(async_engine: AsyncEngine) -> None:
    async with async_engine.begin() as conn:
        await conn.run_sync(Account.metadata.drop_all)
        await conn.run_sync(Account.metadata.create_all)


def _check_eq(*objects, schema: SchemaBase | None = None):
    if len(objects) < 2:
        raise ValueError('Ожидалось минимум два элемента для сравнения')

    t = lambda x: x  # noqa: E731
    if schema:
        t = schema.model_validate

    for left, right in pairwise(objects):
        assert t(left) == t(right)


@pytest.fixture(scope='session')
def check_eq():
    return _check_eq
