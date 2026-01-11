from sqlalchemy.ext.asyncio import AsyncSession

from application.account.cqs.queries.load import load_account
from application.account.schemas.model import (
    SchemaAccountCurrency,
    SchemaTransferRate,
)
from domain.account.events import AccountEvent
from domain.account.model import Account
from domain.vo.money import TransferRate
from shared.cqs.command import CommandBase
from shared.cqs.parser import auto_parse_kwargs


class UpdateAccountCurrencyCommand(CommandBase):
    currency: SchemaAccountCurrency
    transfer_rate: SchemaTransferRate = TransferRate(1)


@load_account(for_update=True)
@auto_parse_kwargs(command_type=UpdateAccountCurrencyCommand)
async def handle(
    *,
    account: Account,
    db_session: AsyncSession,
    command: UpdateAccountCurrencyCommand,
    **_,  # cur_user, code или account_id
) -> Account:
    if command.currency == account.currency:
        return account

    db_session.add(
        AccountEvent.edit_currency(
            account=account,
            old_currency=account.currency,
            new_currency=command.currency,
            transfer_rate=command.transfer_rate,
        )
    )

    account.update_currency(command.currency, command.transfer_rate)
    await db_session.commit()

    return account
