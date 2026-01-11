import functools
from types import UnionType
from typing import Any

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.cqs.parser import auto_parse_kwargs, parse_kwargs_many
from shared.cqs.query import QueryBase, apply_queries
from shared.errors.application import NotFoundError
from shared.storage.repository import RepositoryBase


def generate_load_handle[T](
    *,
    base_statement: Select[tuple[T]],
    query_types: list[type[QueryBase] | UnionType],
):
    query_type, *additional_query_types = query_types

    @auto_parse_kwargs(query_type=query_type)
    async def handle_load(
        *,
        query: QueryBase,
        db_session: AsyncSession,
        **kwargs,
    ) -> T | None:
        queries = parse_kwargs_many(kwargs, additional_query_types)
        return await db_session.scalar(apply_queries(base_statement, query, *queries))

    return handle_load


def generate_list_handle[T](
    *,
    base_statement: Select[tuple[T]],
    query_types: list[Any],
):
    @auto_parse_kwargs(query_types=query_types)
    async def handle_list(
        *,
        queries: list[QueryBase],
        db_session: AsyncSession,
        **_,
    ) -> list[T]:
        return list(await db_session.scalars(apply_queries(base_statement, *queries)))

    return handle_list


def generate_list_handle_with_cursor[T](
    *,
    base_statement: Select[tuple[T]],
    query_types: list[Any],
    entity_repository_cls: type[RepositoryBase[T]],
):
    @auto_parse_kwargs(query_types=query_types)
    async def handle_list(
        *,
        queries: list[QueryBase],
        db_session: AsyncSession,
        cursor: str | None = None,
        **_,
    ) -> tuple[list[T], str | None]:
        entity_repository = entity_repository_cls(db_session)

        statement = apply_queries(base_statement, *queries)
        statement = entity_repository.apply_cursor(statement, cursor)

        items, new_cursor = await entity_repository.list_cursor(statement, cursor)
        return items, new_cursor and new_cursor.dumps()

    return handle_list


DEFAULT_NOT_FOUND_ERROR = NotFoundError('Object not found')


def generate_load_decorator(handle, pass_as: str, not_found_error: NotFoundError = DEFAULT_NOT_FOUND_ERROR):
    def generator(for_update: bool = False, raise_error: bool = True):
        def decorator(func):
            @functools.wraps(func)
            async def wrapper(**kwargs):
                if kwargs.get(pass_as) is None:
                    kwargs[pass_as] = await handle(**kwargs, for_update=for_update)

                if raise_error and kwargs[pass_as] is None:
                    raise not_found_error

                return await func(**kwargs)

            return wrapper

        return decorator

    return generator
