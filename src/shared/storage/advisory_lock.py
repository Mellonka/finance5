import functools
import hashlib
from collections.abc import Callable
from contextlib import asynccontextmanager
from typing import Any

import asyncpg
import sqlalchemy.exc
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


def get_lock_key(lock_name: str) -> int:
    hash_bytes = hashlib.sha256(lock_name.encode()).digest()
    return int.from_bytes(hash_bytes[:8], byteorder='big', signed=True)


@asynccontextmanager
async def advisory_lock(lock_name: str, *, db_session: AsyncSession, lock_timeout=5000):
    lock_key = get_lock_key(lock_name)

    await db_session.execute(text('SET lock_timeout TO :lock_timeout').bindparams(lock_timeout=lock_timeout))

    try:
        await db_session.execute(text('SELECT pg_advisory_xact_lock(:key)').bindparams(key=lock_key))
        yield
    except sqlalchemy.exc.OperationalError as exc:
        if isinstance(exc.orig, asyncpg.LockNotAvailableError):
            raise TimeoutError(f'Таймаут при ожидании блокировки {lock_name}') from exc
        raise


def with_advisory_lock(
    lock_name: str,
    *,
    lock_timeout: int = 5000,
    get_lock_name_suffix: Callable[[dict[str, Any]], str] = lambda _: '',
):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*, db_session: AsyncSession, **kwargs):
            async with advisory_lock(
                f'{lock_name}-{get_lock_name_suffix(kwargs)}', db_session=db_session, lock_timeout=lock_timeout
            ):
                return await func(db_session=db_session, **kwargs)

        return wrapper

    return decorator
