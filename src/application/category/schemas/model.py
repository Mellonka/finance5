from datetime import datetime
from typing import Annotated

from pydantic import Field

from application.user.schemas.model import SchemaUserID
from domain.category.model import (
    CategoryCode,
    CategoryDescription,
    CategoryID,
    CategoryTags,
    CategoryTitle,
    EnumCategoryStatus,
)
from shared.cqs.schemas import SchemaBase

type SchemaCategoryID = CategoryID
type SchemaCategoryCode = Annotated[CategoryCode, Field(min_length=1)]
type SchemaCategoryTitle = Annotated[CategoryTitle, Field(min_length=1)]
type SchemaCategoryDescription = Annotated[CategoryDescription, Field(default=None)]
type SchemaCategoryTags = Annotated[CategoryTags, Field(default_factory=list)]
type SchemaCategoryStatus = Annotated[EnumCategoryStatus, Field(default=EnumCategoryStatus.ACTIVE)]
type SchemaCategoryParentID = Annotated[CategoryID | None, Field(default=None)]


class CategorySchema(SchemaBase):
    id: SchemaCategoryID

    code: SchemaCategoryCode
    user_id: SchemaUserID

    title: SchemaCategoryTitle
    description: SchemaCategoryDescription
    status: SchemaCategoryStatus
    tags: SchemaCategoryTags

    parent_id: SchemaCategoryParentID

    created_at: datetime
    updated_at: datetime
