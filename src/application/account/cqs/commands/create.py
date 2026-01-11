import sqlalchemy
import sqlalchemy.exc
from sqlalchemy.ext.asyncio import AsyncSession

from application.account.errors import AccountIntegrityError
from application.account.schemas.model import (
    SchemaAccountBalance,
    SchemaAccountCode,
    SchemaAccountCurrency,
    SchemaAccountDescription,
    SchemaAccountTags,
    SchemaAccountTitle,
    SchemaAccountType,
)
from domain.account.model import Account
from domain.user.model import User
from shared.cqs.command import CommandBase
from shared.cqs.parser import auto_parse_kwargs


class CreateAccountCommand(CommandBase):
    code: SchemaAccountCode
    title: SchemaAccountTitle
    type: SchemaAccountType
    balance: SchemaAccountBalance
    description: SchemaAccountDescription
    currency: SchemaAccountCurrency
    tags: SchemaAccountTags


@auto_parse_kwargs(command_type=CreateAccountCommand)
async def handle(
    *,
    cur_user: User,
    db_session: AsyncSession,
    command: CreateAccountCommand,
    **_,
) -> Account:
    account = Account(
        code=command.code,
        title=command.title,
        description=command.description,
        type=command.type,
        balance=command.balance,
        currency=command.currency,
        tags=command.tags,
        user_id=cur_user.id,
    )
    db_session.add(account)

    try:
        await db_session.commit()
    except sqlalchemy.exc.IntegrityError as exc:
        raise AccountIntegrityError from exc

    return account
