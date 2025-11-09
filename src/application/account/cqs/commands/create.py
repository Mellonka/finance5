from typing import Any
import sqlalchemy
import sqlalchemy.exc
from sqlalchemy.ext.asyncio import AsyncSession

from application.account.schemas.model import (
    SchemaAccountBalance,
    SchemaAccountCurrency,
    SchemaAccountDescription,
    SchemaAccountName,
    SchemaAccountTags,
    SchemaAccountType,
)
from application.account.cqs.queries.load import auto_handle as load_handle
from domain.account.model import Account
from domain.user.model import User
from shared.cqs.command import CommandBase
from shared.cqs.parser import auto_parse_kwargs
from shared.errors import ConflictError


class CreateAccountCommand(CommandBase):
    name: SchemaAccountName
    type: SchemaAccountType
    balance: SchemaAccountBalance
    description: SchemaAccountDescription
    currency: SchemaAccountCurrency
    tags: SchemaAccountTags


async def handle(*, cur_user: User, db_session: AsyncSession, command: CreateAccountCommand, **_) -> Account:
    account = Account(
        name=command.name,
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
        if await load_handle(db_session=db_session, name=command.name, user_id=cur_user.id):
            raise ConflictError('An account with that name already exists') from exc
        raise

    return account


@auto_parse_kwargs(command_type=CreateAccountCommand)
async def auto_handle(**kwargs: Any) -> Account:
    return await handle(**kwargs)
