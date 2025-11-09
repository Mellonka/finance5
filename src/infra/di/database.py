from typing import AsyncGenerator
from dependency_injector.providers import Configuration, Singleton
from dependency_injector.containers import DeclarativeContainer


from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession


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


async def async_db_session() -> AsyncGenerator[AsyncSession, None]:
    async_session_maker = postgres_container.async_session_maker()
    async with async_session_maker() as db_session:
        yield db_session
