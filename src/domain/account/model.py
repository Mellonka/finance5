from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID

from sqlalchemy import JSON, Numeric, String
from sqlalchemy import UUID as SQLAlchemyUUID
from sqlalchemy.orm import Mapped, mapped_column

from domain.base import Entity
from domain.vo.currency import Currency
from domain.vo.money import Money
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
type AccountName = str
type AccountDescription = str | None
type AccountTags = list[str]


class Account(Entity):
    __tablename__ = 'accounts'

    id: Mapped[AccountID] = mapped_column(SQLAlchemyUUID, default=uuid7, primary_key=True)
    name: Mapped[AccountName] = mapped_column(String(255), unique=True)
    description: Mapped[AccountDescription] = mapped_column(String(255), default=None)
    type: Mapped[EnumAccountType] = mapped_column(default=EnumAccountType.MONEY)
    status: Mapped[EnumAccountStatus] = mapped_column(default=EnumAccountStatus.ACTIVE)
    tags: Mapped[AccountTags] = mapped_column(JSON, default=list)

    balance: Mapped[Money] = mapped_column(Numeric(15, 5), default=Money())
    currency: Mapped[Currency] = mapped_column(String(3), default='RUB')

    created: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))
    updated: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))
