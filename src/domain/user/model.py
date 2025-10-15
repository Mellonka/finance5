from datetime import datetime
from enum import StrEnum
from uuid import UUID

from sqlalchemy import JSON, DateTime, Text
from sqlalchemy import UUID as SQLAlchemyUUID
from sqlalchemy.orm import Mapped, mapped_column

from domain.base import Entity
from shared.utils import uuid7


class EnumUserStatus(StrEnum):
    ACTIVE = 'ACTIVE'
    DISABLED = 'DISABLED'


type UserID = UUID
type UserName = str
type UserDescription = str | None
type UserTags = list[str]


class User(Entity):
    __tablename__ = 'users'

    id: Mapped[UserID] = mapped_column(SQLAlchemyUUID, default=uuid7, primary_key=True)
    name: Mapped[UserName] = mapped_column(Text)
    description: Mapped[UserDescription] = mapped_column(Text, default=None)
    status: Mapped[EnumUserStatus] = mapped_column(default=EnumUserStatus.ACTIVE)
    tags: Mapped[UserTags] = mapped_column(JSON, default=list)

    created: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated: Mapped[datetime] = mapped_column(DateTime(timezone=True))
