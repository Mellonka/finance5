from decimal import Decimal as TransferRate
from typing import Annotated

from pydantic import Field
from pydantic_extra_types.currency_code import ISO4217 as Currency  # noqa: F401

type SchemaTransferRate = Annotated[TransferRate, Field(ge=0)]
