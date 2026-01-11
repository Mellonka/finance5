import functools

from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Singleton
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


class DatabaseContainer(DeclarativeContainer):
    config = Configuration()

    async_engine = Singleton(
        create_async_engine,
        config.async_url,
        echo=config.debug_sql,
    )
    async_session_maker = Singleton(
        async_sessionmaker[AsyncSession],
        async_engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )


postgres_container = DatabaseContainer()


def use_db_session(func):
    @functools.wraps(func)
    async def wrapper(**kwargs):
        if 'db_session' in kwargs:
            return await func(**kwargs)

        if 'async_session_maker' not in kwargs:
            raise ValueError('async_session_maker is required for this function')

        async with kwargs['async_session_maker']() as db_session:
            return await func(db_session=db_session, **kwargs)

    return wrapper
