import datetime as dt
from enum import StrEnum
from uuid import UUID

from sqlalchemy import JSON, DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from domain.account.model import AccountID
from domain.base import Entity
from domain.category.model import CategoryID
from domain.user.model import UserID
from domain.vo.money import Money
from shared.utils import now, uuid7


class EnumTransactionType(StrEnum):
    EXPENSE = 'EXPENSE'
    INCOME = 'INCOME'


type TransactionID = UUID
type TransactionDescription = str | None
type TransactionTags = list[str]


class Transaction(Entity):
    __tablename__ = 'transactions'

    id: Mapped[TransactionID] = mapped_column(default=uuid7, primary_key=True)
    date: Mapped[dt.date] = mapped_column()
    description: Mapped[TransactionDescription] = mapped_column(String(255), default=None)
    tags: Mapped[TransactionTags] = mapped_column(JSON, default=list)
    type: Mapped[EnumTransactionType] = mapped_column(default=EnumTransactionType.EXPENSE)
    user_id: Mapped[UserID] = mapped_column(ForeignKey('users.id'))

    account_id: Mapped[AccountID] = mapped_column(ForeignKey('accounts.id'))
    amount: Mapped[Money] = mapped_column(Numeric(15, 5), default=Money())
    category_id: Mapped[CategoryID] = mapped_column(ForeignKey('categories.id'))

    created: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=now)
