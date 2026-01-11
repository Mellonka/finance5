from typing import get_args

import sqlalchemy.exc
from sqlalchemy.ext.asyncio import AsyncSession

from application.account.cqs.queries.load import load_account
from application.account.errors import AccountIntegrityError
from application.account.schemas.model import (
    SchemaAccountCode,
    SchemaAccountDescription,
    SchemaAccountStatus,
    SchemaAccountTags,
    SchemaAccountTitle,
    SchemaAccountType,
)
from domain.account.model import Account
from shared.cqs.command import CommandBase
from shared.cqs.parser import auto_parse_kwargs


class UpdateAccountCodeCommand(CommandBase):
    code: SchemaAccountCode

    def apply(self, account: Account) -> Account:
        account.code = self.code
        return account


class UpdateAccountTitleCommand(CommandBase):
    title: SchemaAccountTitle

    def apply(self, account: Account) -> Account:
        account.title = self.title
        return account


class UpdateAccountDescriptionCommand(CommandBase):
    description: SchemaAccountDescription

    def apply(self, account: Account) -> Account:
        account.description = self.description
        return account


class UpdateAccountTypeCommand(CommandBase):
    type: SchemaAccountType

    def apply(self, account: Account) -> Account:
        account.type = self.type
        return account


class UpdateAccountTagsCommand(CommandBase):
    tags: SchemaAccountTags

    def apply(self, account: Account) -> Account:
        account.tags = self.tags
        return account


class UpdateAccountStatusCommand(CommandBase):
    status: SchemaAccountStatus

    def apply(self, account: Account) -> Account:
        account.status = self.status
        return account


UpdateAccountCommand = (
    UpdateAccountTitleCommand
    | UpdateAccountCodeCommand
    | UpdateAccountDescriptionCommand
    | UpdateAccountTagsCommand
    | UpdateAccountStatusCommand
    | UpdateAccountTypeCommand
)


@load_account()
@auto_parse_kwargs(command_types=get_args(UpdateAccountCommand))
async def handle(
    *,
    account: Account,
    db_session: AsyncSession,
    commands: list[UpdateAccountCommand],
    **_,  # cur_user, code или account_id
) -> Account:
    for command in commands:
        command.apply(account)

    try:
        await db_session.commit()
    except sqlalchemy.exc.IntegrityError as exc:
        raise AccountIntegrityError from exc

    return account
