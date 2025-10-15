import datetime as dt
from enum import StrEnum, auto
from typing import ClassVar, Literal

from pydantic import BaseModel, ConfigDict
from sqlalchemy import ColumnElement, Select, and_, not_, true
from sqlalchemy.orm import InstrumentedAttribute

from domain.vo.money import Money


class QueryFilterBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    def render_filter(self) -> ColumnElement[bool]:
        raise NotImplementedError


class QueryStatementBase[T](BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    def process_statement(self, statement: Select[tuple[T]]) -> Select[tuple[T]]:
        raise NotImplementedError


type QueryBase = QueryFilterBase | QueryStatementBase


class QueryOnAttrMixin[T](BaseModel):
    _entity_attr: ClassVar[InstrumentedAttribute]

    @classmethod
    def __pydantic_init_subclass__(cls, *, entity_attr: InstrumentedAttribute[T], **_) -> None:
        cls._entity_attr = entity_attr

    @property
    def entity_attr(self) -> InstrumentedAttribute[T]:
        return self.__class__._entity_attr


class DateRangeQueryBase(QueryFilterBase, QueryOnAttrMixin[dt.date]):
    from_date: dt.date | None
    to_date: dt.date | None

    def render_filter(self) -> ColumnElement[bool]:
        return and_(
            self.entity_attr >= self.from_date if self.from_date is not None else true(),
            self.entity_attr <= self.to_date if self.to_date is not None else true(),
        )


class MoneyRangeQueryBase(QueryFilterBase, QueryOnAttrMixin[Money]):
    from_amount: Money | None
    to_amount: Money | None

    def render_filter(self) -> ColumnElement[bool]:
        return and_(
            self.entity_attr >= self.from_amount if self.from_amount is not None else true(),
            self.entity_attr <= self.to_amount if self.to_amount is not None else true(),
        )


class ListFilterType(StrEnum):
    HAVE_ALL = auto()
    HAVE_ANY = auto()
    HAVE_NOTHING = auto()


class TagsQueryBase(QueryFilterBase, QueryOnAttrMixin[list[str]]):
    tags: list[str]
    filter_type: ListFilterType = ListFilterType.HAVE_ANY

    def render_filter(self) -> ColumnElement[bool]:
        match self.filter_type:
            case ListFilterType.HAVE_ALL:
                return self.entity_attr.contains(self.tags)
            case ListFilterType.HAVE_ANY:
                return self.entity_attr.overlap(self.tags)
            case ListFilterType.HAVE_NOTHING:
                return not_(self.entity_attr.overlap(self.tags))

        raise NotImplementedError


class StatusQueryBase[T](QueryFilterBase, QueryOnAttrMixin[T]):
    status: T | list[T]

    def render_filter(self) -> ColumnElement[bool]:
        if isinstance(self.status, list):
            return self.entity_attr.in_(self.status)
        return self.entity_attr == self.status


class TypeQueryBase[T](QueryFilterBase, QueryOnAttrMixin[T]):
    type: T | list[T]

    def render_filter(self) -> ColumnElement[bool]:
        if isinstance(self.type, list):
            return self.entity_attr.in_(self.type)
        return self.entity_attr == self.type


class NameQueryBase[T](QueryFilterBase, QueryOnAttrMixin[T]):
    name: T | list[T]

    def render_filter(self) -> ColumnElement[bool]:
        if isinstance(self.name, list):
            return self.entity_attr.in_(self.name)
        return self.entity_attr == self.name


class OrderByField[T](QueryStatementBase, QueryOnAttrMixin[T]):
    # TODO нужен дискриминатор, иначе не понять что это такое
    type: Literal['sort']
    field: str
    direction: Literal['asc', 'desc'] = 'asc'

    def process_statement(self, statement: Select[tuple[T]]) -> Select[tuple[T]]:
        return statement.order_by(self.entity_attr)
