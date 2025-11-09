from pydantic import BaseModel, ConfigDict
from sqlalchemy import ColumnElement, Select


class QueryBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)


class QueryFilterBase(QueryBase):
    def render_filter(self) -> ColumnElement[bool]:
        raise NotImplementedError


class QueryStatementBase(QueryBase):
    def apply_query(self, statement: Select) -> Select:
        raise NotImplementedError


def apply_queries(statement: Select, *queries: QueryBase) -> Select:
    filters = []
    for query in queries:
        match query:
            case QueryFilterBase():
                filters.append(query.render_filter())
            case QueryStatementBase():
                statement = query.apply_query(statement)

    return statement.where(*filters)
