import asyncpg
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
from domain.account.model import Account
from domain.user.model import UserID
from shared.cqs.base import CommandBase
from shared.errors.model import ConflictError


class CreateAccountCommand(CommandBase):
    name: SchemaAccountName
    type: SchemaAccountType
    balance: SchemaAccountBalance
    description: SchemaAccountDescription
    currency: SchemaAccountCurrency
    tags: SchemaAccountTags
    user_id: UserID


async def handle(*, command: CreateAccountCommand, db_session: AsyncSession, **_) -> Account:
    account = Account(
        name=command.name,
        description=command.description,
        type=command.type,
        balance=command.balance,
        currency=command.currency,
        tags=command.tags,
        user_id=command.user_id,
    )
    db_session.add(account)

    try:
        await db_session.commit()
    except (asyncpg.UniqueViolationError, sqlalchemy.exc.IntegrityError) as exc:
        raise ConflictError from exc

    return account
