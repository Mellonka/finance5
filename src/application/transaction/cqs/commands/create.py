from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession

from application.account.schemas.model import SchemaAccountID
from application.category.schemas.model import SchemaCategoryID
from application.transaction.schemas.model import (
    SchemaTransactionDescription,
    SchemaTransactionTags,
    SchemaTransactionType,
    SchemaTransactionAmount,
)
from domain.transaction.model import Transaction
from domain.user.model import UserID
from shared.cqs.command import CommandBase


class CreateTransactionCommand(CommandBase):
    date: date
    description: SchemaTransactionDescription
    tags: SchemaTransactionTags
    type: SchemaTransactionType
    user_id: UserID
    account_id: SchemaAccountID
    category_id: SchemaCategoryID
    amount: SchemaTransactionAmount


async def handle(*, command: CreateTransactionCommand, db_session: AsyncSession, **_) -> Transaction:
    transaction = Transaction(
        date=command.date,
        description=command.description,
        tags=command.tags,
        type=command.type,
        user_id=command.user_id,
        account_id=command.account_id,
        category_id=command.category_id,
        amount=command.amount,
    )

    db_session.add(transaction)
    await db_session.commit()

    return transaction
