from typing import Annotated

from pydantic import AfterValidator, Field

from application.user.schemas.model import SchemaUserID
from domain.account.model import (
    AccountDescription,
    AccountID,
    AccountName,
    AccountTags,
    EnumAccountStatus,
    EnumAccountType,
)
from domain.vo.currency import Currency
from domain.vo.money import Money
from shared.cqs.base import SchemaBase

type SchemaAccountID = AccountID
type SchemaAccountName = Annotated[AccountName, Field(min_length=1)]
type SchemaAccountDescription = Annotated[AccountDescription, Field(default=None)]
type SchemaAccountType = Annotated[EnumAccountType, Field(default=EnumAccountType.MONEY)]
type SchemaAccountStatus = Annotated[EnumAccountStatus, Field(default=EnumAccountStatus.ACTIVE)]
type SchemaAccountTags = Annotated[AccountTags, Field(default_factory=list)]
type SchemaAccountCurrency = Annotated[Currency, Field(default='RUB')]
type SchemaAccountBalance = Annotated[
    Money, AfterValidator(lambda m: m.quantize(Money('1.00000'))), Field(default=Money(), ge=0)
]


class AccountSchema(SchemaBase):
    id: SchemaAccountID
    name: SchemaAccountName
    description: SchemaAccountDescription
    type: SchemaAccountType
    status: SchemaAccountStatus
    tags: SchemaAccountTags
    user_id: SchemaUserID

    currency: SchemaAccountCurrency
    balance: SchemaAccountBalance

    # created: datetime
    # updated: datetime
