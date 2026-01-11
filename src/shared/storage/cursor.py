import base64
import json
from dataclasses import astuple, dataclass, field
from enum import StrEnum
from typing import Any, Self


class EnumDirection(StrEnum):
    ASC = 'ASC'
    DESC = 'DESC'


@dataclass(slots=True, frozen=True)
class CursorValue:
    field_name: str
    direction: EnumDirection
    value: Any


@dataclass(slots=True)
class Cursor:
    values: list[CursorValue] = field(default_factory=list)

    def dumps(self):
        return base64.b64encode(json.dumps([astuple(value) for value in self.values]).encode()).decode()

    @classmethod
    def loads(cls, cursor_str: str) -> Self:
        return cls([CursorValue(*val) for val in json.loads(base64.b64decode(cursor_str).decode())])
