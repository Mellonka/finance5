import datetime as dt
from enum import StrEnum
from uuid import UUID

from sqlalchemy import UUID as SQLAlchemyUUID
from sqlalchemy import BigInteger, DateTime, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from domain.base import Entity
from shared.utils import uuid7


class EnumUserStatus(StrEnum):
    ACTIVE = 'ACTIVE'
    DISABLED = 'DISABLED'


type UserID = UUID
type UserNickname = str
type UserDescription = str | None
type UserTags = list[str]


class User(Entity):
    __tablename__ = 'users'

    id: Mapped[UserID] = mapped_column(SQLAlchemyUUID, default=uuid7, primary_key=True)
    nickname: Mapped[UserNickname] = mapped_column(Text, unique=True)
    status: Mapped[EnumUserStatus] = mapped_column(default=EnumUserStatus.ACTIVE)

    lsn: Mapped[int] = mapped_column(BigInteger, onupdate=func.next_val())
    serial: Mapped[int] = mapped_column(BigInteger, server_default=func.next_val())
    created: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now())
