import asyncpg
import sqlalchemy.exc
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
from shared.cqs.base import CommandBase
from shared.errors.model import ConflictError


class CreateAccountCommand(CommandBase):
    name: SchemaAccountName
    type: SchemaAccountType
    balance: SchemaAccountBalance
    description: SchemaAccountDescription
    currency: SchemaAccountCurrency
    tags: SchemaAccountTags


async def handle(*, command: CreateAccountCommand, db_session: AsyncSession, **_) -> Account:
    account = Account(
        name=command.name,
        description=command.description,
        type=command.type,
        balance=command.balance,
        currency=command.currency,
        tags=command.tags,
    )
    db_session.add(account)

    try:
        await db_session.commit()
    except (asyncpg.UniqueViolationError, sqlalchemy.exc.IntegrityError) as exc:
        raise ConflictError from exc

    return account
