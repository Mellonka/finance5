from functools import wraps
from typing import Any, Sequence

from pydantic import BaseModel, ValidationError
from shared.cqs.command import CommandBase
from shared.cqs.query import QueryBase
from shared.cqs.schemas import get_type_adapter


class EmptySchema(BaseModel):
    """Для пустых kwargs"""


def parse_kwargs[T](kwargs: dict[str, Any], type: type[T]) -> T | None:
    type_adapter = get_type_adapter(EmptySchema | type)

    try:
        parsed = type_adapter.validate_python(kwargs)
    except ValidationError:
        return
    else:
        if not isinstance(parsed, EmptySchema):
            return parsed


def parse_kwargs_many[T](kwargs: dict[str, Any], types: Sequence[type[T]]) -> list[T]:
    return [parsed for t in types if (parsed := parse_kwargs(kwargs, t))]


def auto_parse_kwargs(
    *,
    command_type: Any | None = None,
    command_types: Sequence[type[CommandBase]] | None = None,
    query_type: Any | None = None,
    query_types: Sequence[type[QueryBase]] | None = None,
):
    def decorator(func):
        @wraps(func)
        async def wrapper(**kwargs: Any):
            if (
                command_type is not None
                and not kwargs.get('command')
                and (command := parse_kwargs(kwargs, command_type))
            ):
                kwargs['command'] = command

            if command_types is not None and (commands := parse_kwargs_many(kwargs, command_types)):
                kwargs.setdefault('commands', [])
                kwargs['commands'].extend(commands)

            if query_type is not None and not kwargs.get('query') and (query := parse_kwargs(kwargs, query_type)):
                kwargs['query'] = query

            if query_types is not None and (queries := parse_kwargs_many(kwargs, query_types)):
                kwargs.setdefault('queries', [])
                kwargs['queries'].extend(queries)

            return await func(**kwargs)

        return wrapper

    return decorator
