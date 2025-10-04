import datetime as dt

from sqlalchemy.ext.asyncio import AsyncSession

from application.account.schemas.model import SchemaAccountID
from application.category.schemas.model import SchemaCategoryID
from application.transaction.schemas.model import (
    SchemaTransactionAmount,
    SchemaTransactionDescription,
    SchemaTransactionTags,
    SchemaTransactionType,
)
from domain.transaction.model import Transaction
from shared.cqs.base import CommandBase


class UpdateTransactionCommandBase(CommandBase):
    def apply(self, transaction: Transaction) -> Transaction:
        raise NotImplementedError


class UpdateTransactionDateCommand(UpdateTransactionCommandBase):
    date: dt.date

    def apply(self, transaction: Transaction) -> Transaction:
        transaction.date = self.date
        return transaction


class UpdateTransactionDescriptionCommand(UpdateTransactionCommandBase):
    description: SchemaTransactionDescription

    def apply(self, transaction: Transaction) -> Transaction:
        transaction.description = self.description
        return transaction


class UpdateTransactionTagsCommand(UpdateTransactionCommandBase):
    tags: SchemaTransactionTags

    def apply(self, transaction: Transaction) -> Transaction:
        transaction.tags = self.tags
        return transaction


class UpdateTransactionTypeCommand(UpdateTransactionCommandBase):
    type: SchemaTransactionType

    def apply(self, transaction: Transaction) -> Transaction:
        transaction.type = self.type
        return transaction


class UpdateTransactionCategoryCommand(UpdateTransactionCommandBase):
    category_id: SchemaCategoryID

    def apply(self, transaction: Transaction) -> Transaction:
        transaction.category_id = self.category_id
        return transaction


class UpdateTransactionAccountCommand(UpdateTransactionCommandBase):
    account_id: SchemaAccountID

    def apply(self, transaction: Transaction) -> Transaction:
        transaction.account_id = self.account_id
        return transaction


class UpdateTransactionAmountCommand(UpdateTransactionCommandBase):
    amount: SchemaTransactionAmount

    def apply(self, transaction: Transaction) -> Transaction:
        transaction.amount = self.amount
        return transaction


type UpdateTransactionCommand = (
    UpdateTransactionDateCommand
    | UpdateTransactionDescriptionCommand
    | UpdateTransactionTypeCommand
    | UpdateTransactionTagsCommand
    | UpdateTransactionCategoryCommand
    | UpdateTransactionAccountCommand
    | UpdateTransactionAmountCommand
)


async def handle(
    *, transaction: Transaction, db_session: AsyncSession, commands: list[UpdateTransactionCommand], **_
) -> Transaction:
    if not commands:
        return transaction

    db_session.add(transaction)

    for command in commands:
        command.apply(transaction)
    transaction.updated = dt.datetime.now(dt.UTC)

    await db_session.commit()

    return transaction
