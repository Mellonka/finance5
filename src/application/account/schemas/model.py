import datetime as dt
from typing import Annotated

from pydantic import AfterValidator, Field
from pydantic_extra_types.currency_code import Currency as SchemaCurrency

from application.user.schemas.model import SchemaUserID
from domain.account.model import (
    AccountCode,
    AccountDescription,
    AccountID,
    AccountTags,
    AccountTitle,
    EnumAccountStatus,
    EnumAccountType,
)
from domain.vo.money import Money, TransferRate
from shared.cqs.schemas import SchemaBase

type SchemaAccountID = AccountID
type SchemaAccountCode = Annotated[AccountCode, Field(min_length=1)]
type SchemaAccountTitle = Annotated[AccountTitle, Field(min_length=1)]
type SchemaAccountDescription = Annotated[AccountDescription, Field(default=None)]
type SchemaAccountType = Annotated[EnumAccountType, Field(default=EnumAccountType.MONEY)]
type SchemaAccountStatus = Annotated[EnumAccountStatus, Field(default=EnumAccountStatus.ACTIVE)]
type SchemaAccountTags = Annotated[AccountTags, Field(default_factory=list)]
type SchemaAccountCurrency = Annotated[SchemaCurrency, Field(default='RUB')]
type SchemaTransferRate = Annotated[TransferRate, Field(ge=0)]
type SchemaAccountBalance = Annotated[
    Money,
    AfterValidator(lambda m: m.quantize(Money('1.0000'))),
    Field(default=Money(), ge=0),
]
type SchemaAccountTransferAmount = Annotated[
    Money,
    AfterValidator(lambda m: m.quantize(Money('1.0000'))),
    Field(default=Money(), ge=0),
]


class AccountSchema(SchemaBase):
    id: SchemaAccountID

    code: SchemaAccountCode
    user_id: SchemaUserID

    title: SchemaAccountTitle
    description: SchemaAccountDescription
    type: SchemaAccountType
    status: SchemaAccountStatus
    tags: SchemaAccountTags

    currency: SchemaAccountCurrency
    balance: SchemaAccountBalance

    updated_at: dt.datetime
    created_at: dt.datetime
