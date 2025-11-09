import datetime as dt
from enum import StrEnum
from uuid import UUID

from sqlalchemy import JSON, BigInteger, DateTime, ForeignKey, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domain.account.model import Account, AccountID
from domain.base import Entity
from domain.category.model import Category, CategoryID
from domain.user.model import UserID
from domain.vo.money import Money
from shared.utils import uuid7


class EnumTransactionType(StrEnum):
    EXPENSE = 'EXPENSE'
    INCOME = 'INCOME'


class EnumTransactionStatus(StrEnum):
    PENDING = 'PENDING'
    COMPLETED = 'COMPLETED'
    CANCELLED = 'CANCELLED'


type TransactionID = UUID
type TransactionDescription = str | None
type TransactionTags = list[str]


class Transaction(Entity):
    __tablename__ = 'transactions'

    id: Mapped[TransactionID] = mapped_column(default=uuid7, primary_key=True)
    date: Mapped[dt.date] = mapped_column()
    description: Mapped[TransactionDescription] = mapped_column(Text, default=None)
    tags: Mapped[TransactionTags] = mapped_column(JSON, default=list)
    type: Mapped[EnumTransactionType] = mapped_column(default=EnumTransactionType.EXPENSE)
    status: Mapped[EnumTransactionStatus] = mapped_column(default=EnumTransactionStatus.PENDING)
    user_id: Mapped[UserID] = mapped_column(ForeignKey('users.id'))

    amount: Mapped[Money] = mapped_column(Numeric(15, 5), default=Money())

    account_id: Mapped[AccountID] = mapped_column(ForeignKey('accounts.id'))
    account: Mapped[Account] = relationship()

    category_id: Mapped[CategoryID] = mapped_column(ForeignKey('categories.id'))
    category: Mapped[Category] = relationship()

    lsn: Mapped[int] = mapped_column(BigInteger)
    serial: Mapped[int] = mapped_column(BigInteger)
    updated: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True))
    created: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True))
