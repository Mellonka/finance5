import datetime as dt
from enum import StrEnum
from uuid import UUID

from sqlalchemy import JSON, BigInteger, DateTime, ForeignKey, Numeric, Text, UniqueConstraint, func
from sqlalchemy import UUID as SQLAlchemyUUID
from sqlalchemy.orm import Mapped, mapped_column

from domain.base import Entity
from domain.user.model import UserID
from domain.vo.money import Currency, Money, TransferRate
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
    user_id: Mapped[UserID] = mapped_column(SQLAlchemyUUID, ForeignKey('users.id'))

    title: Mapped[AccountTitle] = mapped_column(Text)
    description: Mapped[AccountDescription] = mapped_column(Text, default=None)
    tags: Mapped[AccountTags] = mapped_column(JSON, default=list)
    type: Mapped[EnumAccountType] = mapped_column(default=EnumAccountType.MONEY)
    status: Mapped[EnumAccountStatus] = mapped_column(default=EnumAccountStatus.ACTIVE)

    balance: Mapped[Money] = mapped_column(Numeric(19, 4), default=Money())
    currency: Mapped[Currency] = mapped_column(Text, default='RUB')

    lsn: Mapped[int] = mapped_column(BigInteger, onupdate=func.next_val())
    serial: Mapped[int] = mapped_column(BigInteger, server_default=func.next_val())
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (UniqueConstraint(user_id, code),)

    def update_currency(self, currency: Currency, transfer_rate: TransferRate) -> None:
        self.currency = currency
        self.balance *= transfer_rate
