from enum import StrEnum
from uuid import UUID

from sqlalchemy import JSON, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domain.base import Entity
from shared.utils import uuid7


class EnumCategoryType(StrEnum):
    EXPENSE = 'EXPENSE'
    INCOME = 'INCOME'
    TRANSFER = 'TRANSFER'


class EnumCategoryStatus(StrEnum):
    ACTIVE = 'ACTIVE'
    DISABLED = 'DISABLED'


type CategoryID = UUID
type CategoryName = str
type CategoryDescription = str | None
type CategoryTags = list[str]


class Category(Entity):
    __tablename__ = 'categories'

    id: Mapped[CategoryID] = mapped_column(default=uuid7, primary_key=True)
    name: Mapped[CategoryName] = mapped_column(String(255), unique=True)
    description: Mapped[CategoryDescription] = mapped_column(String(255), nullable=True, default=None)
    tags: Mapped[CategoryTags] = mapped_column(JSON, default=list)
    type: Mapped[EnumCategoryType] = mapped_column(default=EnumCategoryType.EXPENSE)
    status: Mapped[EnumCategoryStatus] = mapped_column(default=EnumCategoryStatus.ACTIVE)

    parent_id: Mapped[CategoryID | None] = mapped_column(ForeignKey('categories.id'))

    parent: Mapped['Category | None'] = relationship('Category', back_populates='children', remote_side=[id])
    children: Mapped[list['Category']] = relationship('Category', back_populates='parent')
