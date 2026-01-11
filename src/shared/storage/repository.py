from collections.abc import AsyncIterable
from dataclasses import dataclass
from typing import Any

from sqlalchemy import Select, UnaryExpression, and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute

from shared.errors.application import NotFoundError
from shared.storage.cursor import Cursor, CursorValue, EnumDirection
from shared.storage.filters import FilterHandler


@dataclass(slots=True, init=False)
class RepositoryConfig[T]:
    entity_cls: type[T]
    primary_key: tuple[InstrumentedAttribute]
    filter_handlers: list[type[FilterHandler[T]]]
    default_limit: int
    default_filters: dict[str, Any]

    def __init__(
        self,
        *,
        entity_cls: type[T],
        primary_key: InstrumentedAttribute | tuple[InstrumentedAttribute],
        filter_handlers: list[type[FilterHandler[T]]] | None = None,
        default_filters: dict[str, Any] | None = None,
        default_limit: int = 100,
    ) -> None:
        self.entity_cls = entity_cls
        self.primary_key = primary_key if isinstance(primary_key, tuple) else (primary_key,)
        self.filter_handlers = filter_handlers or []
        self.default_filters = default_filters or {}
        self.default_limit = default_limit


@dataclass(slots=True)
class RepositoryBase[T]:
    db_session: AsyncSession

    def __init_subclass__(cls, config: RepositoryConfig[T]) -> None:
        cls.config = config

    @classmethod
    def apply_filters(cls, statement: Select[tuple[T]], filters: dict[str, Any]) -> Select[tuple[T]]:
        all_filters = filters | cls.config.default_filters
        for custom_filter in cls.config.filter_handlers:
            statement = custom_filter.process_filters(cls.config.entity_cls, statement, all_filters)
        return statement.filter_by(**filters)

    @classmethod
    def select(cls, **filters) -> Select[tuple[T]]:
        if filters:
            return cls.apply_filters(select(cls.config.entity_cls), filters)
        return select(cls.config.entity_cls)

    async def load(self, *pkey: Any) -> T | None:
        if len(pkey) != len(self.config.primary_key):
            raise ValueError

        return await self.db_session.scalar(
            self.select().where(*(attr == value for attr, value in zip(self.config.primary_key, pkey)))
        )

    async def load_by(self, **filters) -> T | None:
        return await self.db_session.scalar(self.select(**filters))

    async def exists(self, **filters) -> bool:
        return await self.db_session.scalar(self.select(**filters).exists().select())  # type: ignore

    @classmethod
    def apply_cursor(cls, statement: Select[tuple[T]], cursor: Cursor | str | None = None) -> Select[tuple[T]]:
        if not cursor:
            return statement

        if isinstance(cursor, str):
            cursor = Cursor.loads(cursor)

        conditions = list[Any]()
        eq_conditions = list[Any]()

        for cursor_value in cursor.values:
            eq_conditions.append(getattr(cls.config.entity_cls, cursor_value.field_name) == cursor_value.value)

        for cursor_value in reversed(cursor.values):
            eq_conditions.pop()

            if cursor_value.direction == EnumDirection.ASC:
                condition = getattr(cls.config.entity_cls, cursor_value.field_name) > cursor_value.value
            else:
                condition = getattr(cls.config.entity_cls, cursor_value.field_name) < cursor_value.value

            conditions.append(and_(*eq_conditions, condition))

        return statement.where(or_(*conditions))

    async def list_cursor(
        self, statement: Select[tuple[T]], cursor: Cursor | str | None = None
    ) -> tuple[list[T], Cursor | None]:
        if not statement._order_by_clauses:
            raise ValueError('Order is required for cursor')

        statement = self.apply_cursor(statement, cursor)

        if statement._limit_clause is None:
            statement = statement.limit(self.config.default_limit)

        if not (items := list(await self.db_session.scalars(statement))):
            return items, None

        cursor = Cursor()
        for col in statement._order_by_clauses:
            if isinstance(col, UnaryExpression):  # UGLY
                direction = EnumDirection.ASC if col.modifier.__name__ == 'asc_op' else EnumDirection.DESC  # type: ignore
                cursor.values.append(CursorValue(col.element.name, direction, getattr(items[-1], col.element.name)))  # type: ignore
            else:
                # Plain column without explicit ordering
                cursor.values.append(CursorValue(col.name, EnumDirection.ASC, getattr(items[-1], col.name)))  # type: ignore

        return items, cursor

    async def ilist(self, statement: Select[tuple[T]], cursor: Cursor | str | None = None) -> AsyncIterable[T]:
        while True:
            items, cursor = await self.list_cursor(statement, cursor)
            if not items:
                return
            for item in items:
                yield item

    async def ibatch(self, statement: Select[tuple[T]], cursor: Cursor | str | None = None) -> AsyncIterable[list[T]]:
        while True:
            items, cursor = await self.list_cursor(statement, cursor)
            if not items:
                return
            yield items

    async def list_full(self, statement: Select[tuple[T]]) -> list[T]:
        return list(await self.db_session.scalars(statement))

    async def load_or_error(self, *pkey: Any) -> T:
        if entity := await self.load(*pkey):
            return entity
        raise NotFoundError

    async def load_by_or_error(self, **filters) -> T:
        if entity := await self.load_by(**filters):
            return entity
        raise NotFoundError
