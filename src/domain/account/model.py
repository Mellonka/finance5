from datetime import datetime
from enum import StrEnum
from uuid import UUID

from sqlalchemy import JSON, ForeignKey, Numeric, Text, UniqueConstraint, DateTime
from sqlalchemy import UUID as SQLAlchemyUUID
from sqlalchemy.orm import Mapped, mapped_column

from domain.base import Entity
from domain.user.model import UserID
from domain.vo.money import Currency, Money
from shared.utils import uuid7


class EnumAccountStatus(StrEnum):
    ACTIVE = 'ACTIVE'
    DISABLED = 'DISABLED'


class EnumAccountType(StrEnum):
    GOAL = 'GOAL'
    LOAN = 'LOAN'
    SAVINGS = 'SAVINGS'
    INVESTMENT = 'INVESTMENT'
    MONEY = 'MONEY'


type AccountID = UUID
type AccountCode = str
type AccountTitle = str
type AccountDescription = str | None
type AccountTags = list[str]


class Account(Entity):
    __tablename__ = 'accounts'

    id: Mapped[AccountID] = mapped_column(SQLAlchemyUUID, default=uuid7, primary_key=True)
    code: Mapped[AccountCode] = mapped_column(Text)
    title: Mapped[AccountTitle] = mapped_column(Text)
    description: Mapped[AccountDescription] = mapped_column(Text, default=None)
    tags: Mapped[AccountTags] = mapped_column(JSON, default=list)
    type: Mapped[EnumAccountType] = mapped_column(default=EnumAccountType.MONEY)
    status: Mapped[EnumAccountStatus] = mapped_column(default=EnumAccountStatus.ACTIVE)
    user_id: Mapped[UserID] = mapped_column(SQLAlchemyUUID, ForeignKey('users.id'))

    balance: Mapped[Money] = mapped_column(Numeric(15, 5), default=Money())
    currency: Mapped[Currency] = mapped_column(Text, default='RUB')

    created: Mapped[datetime] = mapped_column(DateTime(), default=datetime.now)
    updated: Mapped[datetime] = mapped_column(DateTime(), default=datetime.now)

    __table_args__ = (UniqueConstraint(user_id, code),)


Account.id
