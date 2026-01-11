from sqlalchemy.ext.asyncio import AsyncSession

from application.account.cqs.queries.load import load_account
from application.account.schemas.model import (
    SchemaAccountBalance,
)
from domain.account.events import AccountEvent
from domain.account.model import Account
from shared.cqs.command import CommandBase
from shared.cqs.parser import auto_parse_kwargs


class UpdateAccountBalanceCommand(CommandBase):
    balance: SchemaAccountBalance


@load_account(for_update=True)
@auto_parse_kwargs(command_type=UpdateAccountBalanceCommand)
async def handle(
    *,
    account: Account,
    db_session: AsyncSession,
    command: UpdateAccountBalanceCommand,
    **_,  # cur_user, code или account_id
) -> Account:
    if account.balance == command.balance:
        return account

    db_session.add(
        AccountEvent.balance_adjustment(
            account=account,
            old_balance=account.balance,
            new_balance=command.balance,
        )
    )

    account.balance = command.balance
    await db_session.commit()

    return account
