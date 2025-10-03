from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy import JSON, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from domain.account.model import AccountID
from domain.base import Entity
from domain.category.model import CategoryID
from shared.utils import uuid7

type TransactionID = UUID
type TransactionDescription = str | None
type TransactionTags = list[str]


class Transaction(Entity):
    __tablename__ = 'transactions'

    id: Mapped[TransactionID] = mapped_column(default=uuid7, primary_key=True)
    date: Mapped[date]
    description: Mapped[TransactionDescription] = mapped_column(String(255), default=None)

    f_account_id: Mapped[AccountID] = mapped_column(ForeignKey('accounts.id'))
    t_account_id: Mapped[AccountID | None] = mapped_column(ForeignKey('accounts.id'))

    amount: Mapped[Decimal] = mapped_column(Numeric(15, 5), default=Decimal())
    transfer_rate: Mapped[Decimal] = mapped_column(Numeric(15, 5), default=1)

    category_id: Mapped[CategoryID] = mapped_column(ForeignKey('categories.id'))

    tags: Mapped[TransactionTags] = mapped_column(JSON, default=list)
