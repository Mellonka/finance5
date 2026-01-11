import datetime as dt
from enum import StrEnum

from sqlalchemy import JSON, BigInteger, DateTime, ForeignKey, Text, func
from sqlalchemy import UUID as SQLAlchemyUUID
from sqlalchemy.orm import Mapped, mapped_column

from domain.account.model import Account, AccountID
from domain.base import Entity
from domain.user.model import UserID
from domain.vo.money import Currency, Money, TransferRate


class EnumAccountEvent(StrEnum):
    EDIT_CURRENCY = 'EDIT_CURRENCY'

    TRANSFER_MONEY_SRC = 'TRANSFER_MONEY_SRC'
    TRANSFER_MONEY_DST = 'TRANSFER_MONEY_DST'

    BALANCE_ADJUSTMENT = 'BALANCE_ADJUSTMENT'


type AccountEventEvent = str
type AccountEventData = dict


class AccountEvent(Entity):
    __tablename__ = 'account_events'

    serial: Mapped[int] = mapped_column(BigInteger, autoincrement=True, primary_key=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user_id: Mapped[UserID] = mapped_column(SQLAlchemyUUID, ForeignKey('users.id'))
    account_id: Mapped[AccountID] = mapped_column(SQLAlchemyUUID, ForeignKey('accounts.id'))

    data: Mapped[AccountEventData] = mapped_column(JSON)
    event: Mapped[AccountEventEvent] = mapped_column(Text)

    @classmethod
    def transfer_money(
        cls,
        *,
        amount: Money,
        src_account: Account,
        dst_account: Account,
        transfer_rate: TransferRate,
    ) -> tuple['AccountEvent', 'AccountEvent']:
        return cls(
            account_id=src_account.id,
            user_id=src_account.user_id,
            event=EnumAccountEvent.TRANSFER_MONEY_SRC,
            data={
                'amount': amount,
                'src_account_id': src_account.id,
                'dst_account_id': dst_account.id,
                'transfer_rate': transfer_rate,
            },
        ), cls(
            account_id=dst_account.id,
            user_id=dst_account.user_id,
            event=EnumAccountEvent.TRANSFER_MONEY_DST,
            data={
                'amount': amount,
                'src_account_id': src_account.id,
                'dst_account_id': dst_account.id,
                'transfer_rate': transfer_rate,
            },
        )

    @classmethod
    def balance_adjustment(
        cls,
        *,
        account: Account,
        old_balance: Money,
        new_balance: Money,
    ) -> 'AccountEvent':
        return cls(
            account_id=account.id,
            user_id=account.user_id,
            event=EnumAccountEvent.BALANCE_ADJUSTMENT,
            data={
                'old_balance': old_balance,
                'new_balance': new_balance,
            },
        )

    @classmethod
    def edit_currency(
        cls,
        *,
        account: Account,
        new_currency: Currency,
        old_currency: Currency,
        transfer_rate: TransferRate,
    ) -> 'AccountEvent':
        return cls(
            account_id=account.id,
            user_id=account.user_id,
            event=EnumAccountEvent.EDIT_CURRENCY,
            data={
                'new_currency': new_currency,
                'old_currency': old_currency,
                'transfer_rate': transfer_rate,
            },
        )
