import datetime as dt
from enum import StrEnum
from uuid import UUID

from sqlalchemy import JSON, BigInteger, DateTime, ForeignKey, Text, UniqueConstraint, func
from sqlalchemy import UUID as SQLAlchemyUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domain.base import Entity
from domain.user.model import UserID
from shared.utils import uuid7


class EnumCategoryStatus(StrEnum):
    ACTIVE = 'ACTIVE'
    DISABLED = 'DISABLED'


type CategoryID = UUID
type CategoryCode = str
type CategoryTitle = str
type CategoryDescription = str | None
type CategoryTags = list[str]


class Category(Entity):
    __tablename__ = 'categories'

    id: Mapped[CategoryID] = mapped_column(SQLAlchemyUUID, default=uuid7, primary_key=True)

    code: Mapped[CategoryCode] = mapped_column(Text)
    user_id: Mapped[UserID] = mapped_column(ForeignKey('users.id'))

    title: Mapped[CategoryTitle] = mapped_column(Text)
    description: Mapped[CategoryDescription] = mapped_column(Text, default=None)
    tags: Mapped[CategoryTags] = mapped_column(JSON, default=list)
    status: Mapped[EnumCategoryStatus] = mapped_column(default=EnumCategoryStatus.ACTIVE)

    parent_id: Mapped[CategoryID | None] = mapped_column(ForeignKey('categories.id'))
    parent: Mapped['Category | None'] = relationship('Category', back_populates='children', remote_side=[id])
    children: Mapped[list['Category']] = relationship('Category', back_populates='parent')

    lsn: Mapped[int] = mapped_column(BigInteger, onupdate=func.next_val())
    serial: Mapped[int] = mapped_column(BigInteger, server_default=func.next_val())
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (UniqueConstraint(user_id, code),)
