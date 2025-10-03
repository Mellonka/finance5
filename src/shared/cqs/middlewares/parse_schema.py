from collections.abc import Callable
from dataclasses import dataclass
from typing import Sequence

from shared.cqs.base import SchemaBase
from shared.cqs.middlewares.pipeline import MiddlewareBase


@dataclass(slots=True)
class ParseSchemaMiddleware(MiddlewareBase):
    schema_model: type[SchemaBase]

    async def handle(self, next_handle: Callable, **kwargs):
        entities = await next_handle(self, **kwargs)

        if not isinstance(entities, (list, tuple, Sequence)):
            return self.schema_model.model_validate(entities)

        return [self.schema_model.model_validate(entity) for entity in entities]
