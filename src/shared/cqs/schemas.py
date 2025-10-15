from functools import lru_cache
from typing import TypeAliasType

from pydantic import BaseModel, ConfigDict, TypeAdapter


class SchemaBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, from_attributes=True)


@lru_cache(maxsize=None)
def get_type_adapter(field_schema: type | TypeAliasType) -> TypeAdapter:
    return TypeAdapter(field_schema)


def var_validate[T](field_schema: type | TypeAliasType, value: T) -> T:
    return get_type_adapter(field_schema).validate_python(value)
