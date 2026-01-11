from datetime import date, datetime
from typing import Annotated

from pydantic import AfterValidator, Field

from application.account.schemas.model import SchemaAccountID
from application.category.schemas.model import SchemaCategoryID
from application.user.schemas.model import SchemaUserID
from domain.transaction.model import (
    EnumTransactionStatus,
    EnumTransactionType,
    TransactionDescription,
    TransactionID,
    TransactionTags,
)
from domain.vo.money import Money
from shared.cqs.schemas import SchemaBase

type SchemaTransactionID = TransactionID
type SchemaTransactionDescription = Annotated[TransactionDescription, Field(default=None)]
type SchemaTransactionTags = Annotated[TransactionTags, Field(default_factory=list)]
type SchemaTransactionAmount = Annotated[
    Money, AfterValidator(lambda m: m.quantize(Money('1.0000'))), Field(default=Money(), ge=0)
]
type SchemaTransactionType = Annotated[EnumTransactionType, Field(default=EnumTransactionType.EXPENSE)]
type SchemaTransactionStatus = Annotated[EnumTransactionStatus, Field(default=EnumTransactionStatus.PENDING)]


class TransactioSchemaBase(SchemaBase):
    id: SchemaTransactionID
    date: date
    description: SchemaTransactionDescription
    tags: SchemaTransactionTags
    type: SchemaTransactionType
    status: SchemaTransactionStatus
    user_id: SchemaUserID

    account_id: SchemaAccountID
    category_id: SchemaCategoryID
    amount: SchemaTransactionAmount

    created: datetime
    updated: datetime
