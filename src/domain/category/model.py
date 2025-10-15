from datetime import datetime
from enum import StrEnum
from uuid import UUID

from sqlalchemy import JSON, DateTime, ForeignKey, Text, UUID as SQLAlchemyUUID, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domain.base import Entity
from domain.user.model import UserID
from shared.utils import uuid7


class EnumCategoryStatus(StrEnum):
    ACTIVE = 'ACTIVE'
    DISABLED = 'DISABLED'


type CategoryID = UUID
type CategoryName = str
type CategoryDescription = str | None
type CategoryTags = list[str]


class Category(Entity):
    __tablename__ = 'categories'

    id: Mapped[CategoryID] = mapped_column(SQLAlchemyUUID, default=uuid7, primary_key=True)
    name: Mapped[CategoryName] = mapped_column(Text, unique=True)
    description: Mapped[CategoryDescription] = mapped_column(Text, default=None)
    tags: Mapped[CategoryTags] = mapped_column(JSON, default=list)
    status: Mapped[EnumCategoryStatus] = mapped_column(default=EnumCategoryStatus.ACTIVE)
    user_id: Mapped[UserID] = mapped_column(ForeignKey('users.id'))

    parent_id: Mapped[CategoryID | None] = mapped_column(ForeignKey('categories.id'))

    parent: Mapped['Category | None'] = relationship('Category', back_populates='children', remote_side=[id])
    children: Mapped[list['Category']] = relationship('Category', back_populates='parent')

    created: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    __table_args__ = (UniqueConstraint(user_id, name),)
