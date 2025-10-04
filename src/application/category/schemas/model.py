from datetime import datetime
from typing import Annotated

from pydantic import Field

from application.user.schemas.model import SchemaUserID
from domain.category.model import (
    CategoryDescription,
    CategoryID,
    CategoryName,
    CategoryTags,
    EnumCategoryStatus,
)
from shared.cqs.base import SchemaBase

type SchemaCategoryID = CategoryID
type SchemaCategoryName = Annotated[CategoryName, Field(min_length=1)]
type SchemaCategoryDescription = Annotated[CategoryDescription, Field(default=None)]
type SchemaCategoryTags = Annotated[CategoryTags, Field(default_factory=list)]
type SchemaCategoryStatus = Annotated[EnumCategoryStatus, Field(default=EnumCategoryStatus.ACTIVE)]
type SchemaCategoryParentID = Annotated[CategoryID | None, Field(default=None)]


class CategorySchema(SchemaBase):
    id: SchemaCategoryID
    name: SchemaCategoryName
    description: SchemaCategoryDescription
    status: SchemaCategoryStatus
    tags: SchemaCategoryTags
    user_id: SchemaUserID

    parent_id: SchemaCategoryParentID

    created: datetime
    updated: datetime
