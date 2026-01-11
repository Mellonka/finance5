from functools import cache

from pydantic import BaseModel, ConfigDict, TypeAdapter


class SchemaBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, from_attributes=True)


@cache
def get_type_adapter(field_schema) -> TypeAdapter:
    return TypeAdapter(field_schema)


def var_validate(field_schema, value):
    return get_type_adapter(field_schema).validate_python(value)
