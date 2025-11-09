from typing import Any, ClassVar
from sqlalchemy import Select
from sqlalchemy.orm import InstrumentedAttribute


class FilterHandler[T]:
    @classmethod
    def process_filters(
        cls, entity_cls: type[T], statement: Select[tuple[T]], filters: dict[str, Any]
    ) -> Select[tuple[T]]:
        for filter_name in list(filters):
            if (handle := getattr(cls, filter_name, None)) is not None:
                statement = handle(entity_cls, statement, filters.pop(filter_name))
        return statement


class UseInForArrays[T](FilterHandler[T]):
    blacklist: ClassVar[set[InstrumentedAttribute]] = set()

    @classmethod
    def process_filters(
        cls, entity_cls: type[T], statement: Select[tuple[T]], filters: dict[str, Any]
    ) -> Select[tuple[T]]:
        for filter_name in list(filters):
            entity_field = getattr(entity_cls, filter_name, None)
            if entity_field and entity_field not in cls.blacklist and isinstance(filters[filter_name], (tuple, list)):
                statement = statement.where(entity_field.in_(filters.pop(filter_name)))

        return statement
