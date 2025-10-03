from datetime import UTC, datetime

import asyncpg
from sqlalchemy.ext.asyncio import AsyncSession

from application.account.cqs.schemas.model import (
    SchemaAccountBalance,
    SchemaAccountCurrency,
    SchemaAccountDescription,
    SchemaAccountName,
    SchemaAccountTags,
    SchemaAccountType,
)
from domain.account.model import Account
from domain.vo.currency import SchemaTransferRate, TransferRate
from shared.cqs.base import CommandBase
from shared.errors.model import ConflictError, NotFoundError


class UpdateAccountCommandBase(CommandBase):
    def apply(self, account: Account) -> Account:
        raise NotImplementedError


class UpdateAccountNameCommand(UpdateAccountCommandBase):
    name: SchemaAccountName

    def apply(self, account: Account) -> Account:
        account.name = self.name
        return account


class UpdateAccountDescriptionCommand(UpdateAccountCommandBase):
    description: SchemaAccountDescription

    def apply(self, account: Account) -> Account:
        account.description = self.description
        return account


class UpdateAccountTypeCommand(UpdateAccountCommandBase):
    type: SchemaAccountType

    def apply(self, account: Account) -> Account:
        account.type = self.type
        return account


class UpdateAccountTagsCommand(UpdateAccountCommandBase):
    tags: SchemaAccountTags

    def apply(self, account: Account) -> Account:
        account.tags = self.tags
        return account


class UpdateAccountBalanceCommand(UpdateAccountCommandBase):
    balance: SchemaAccountBalance

    def apply(self, account: Account) -> Account:
        account.balance = self.balance
        return account


class UpdateAccountCurrencyCommand(UpdateAccountCommandBase):
    currency: SchemaAccountCurrency
    transfer_rate: SchemaTransferRate = TransferRate(1)

    def apply(self, account: Account) -> Account:
        account.balance = account.balance * self.transfer_rate
        account.currency = self.currency
        return account


type UpdateAccountCommand = (
    UpdateAccountNameCommand
    | UpdateAccountDescriptionCommand
    | UpdateAccountTypeCommand
    | UpdateAccountTagsCommand
    | UpdateAccountBalanceCommand
    | UpdateAccountCurrencyCommand
)


async def handle(
    *, account: Account | None, db_session: AsyncSession, commands: list[UpdateAccountCommand], **_
) -> Account:
    if not account:
        raise NotFoundError('Account not found')

    if not commands:
        return account

    db_session.add(account)

    for command in commands:
        command.apply(account)

    account.updated = datetime.now(UTC)

    try:
        await db_session.commit()
    except asyncpg.UniqueViolationError as exc:
        raise ConflictError from exc

    return account
