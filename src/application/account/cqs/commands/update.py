from datetime import datetime
from typing import Any, get_args

from sqlalchemy.ext.asyncio import AsyncSession

from application.account.cqs.queries.load import auto_handle as load_handle
from application.account.schemas.model import (
    SchemaAccountBalance,
    SchemaAccountCurrency,
    SchemaAccountDescription,
    SchemaAccountName,
    SchemaAccountStatus,
    SchemaAccountTags,
    SchemaAccountType,
    SchemaTransferRate,
)
from domain.account.model import Account
from domain.vo.money import TransferRate
from shared.cqs.command import CommandBase
from shared.cqs.parser import auto_parse_kwargs
from shared.errors import ConflictError
from shared.errors.domain import DomainError


class UpdateAccountNameCommand(CommandBase):
    name: SchemaAccountName

    async def checks(self, account: Account, db_session: AsyncSession) -> DomainError | None:
        if self.name != account.code and await load_handle(
            db_session=db_session, user_id=account.user_id, name=self.name
        ):
            return ConflictError('An account with that name already exists')

    async def apply(self, account: Account, db_session: AsyncSession) -> Account:
        if error := await self.checks(account, db_session):
            raise error

        account.code = self.name
        return account


class UpdateAccountDescriptionCommand(CommandBase):
    description: SchemaAccountDescription

    async def apply(self, account: Account, _: AsyncSession) -> Account:
        account.description = self.description
        return account


class UpdateAccountTypeCommand(CommandBase):
    type: SchemaAccountType

    async def apply(self, account: Account, _: AsyncSession) -> Account:
        account.type = self.type
        return account


class UpdateAccountTagsCommand(CommandBase):
    tags: SchemaAccountTags

    async def apply(self, account: Account, _: AsyncSession) -> Account:
        account.tags = self.tags
        return account


class UpdateAccountBalanceCommand(CommandBase):
    balance: SchemaAccountBalance

    async def apply(self, account: Account, _: AsyncSession) -> Account:
        account.balance = self.balance
        return account


class UpdateAccountCurrencyCommand(CommandBase):
    currency: SchemaAccountCurrency
    transfer_rate: SchemaTransferRate = TransferRate(1)

    async def apply(self, account: Account, _: AsyncSession) -> Account:
        account.balance = account.balance * self.transfer_rate
        account.currency = self.currency
        return account


class UpdateAccountStatusCommand(CommandBase):
    status: SchemaAccountStatus

    async def apply(self, account: Account, _: AsyncSession) -> Account:
        account.status = self.status
        return account


UpdateAccountCommand = (
    UpdateAccountNameCommand
    | UpdateAccountDescriptionCommand
    | UpdateAccountTypeCommand
    | UpdateAccountTagsCommand
    | UpdateAccountBalanceCommand
    | UpdateAccountCurrencyCommand
    | UpdateAccountStatusCommand
)


async def handle(*, account: Account, db_session: AsyncSession, commands: list[UpdateAccountCommand], **_) -> Account:
    db_session.add(account)

    for command in commands:
        await command.apply(account, db_session)

    account.updated = datetime.now()
    await db_session.commit()

    return account


@auto_parse_kwargs(command_types=get_args(UpdateAccountCommand))
async def auto_handle(**kwargs: Any) -> Account:
    return await handle(**kwargs)
