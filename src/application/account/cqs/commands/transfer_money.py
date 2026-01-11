from sqlalchemy.ext.asyncio import AsyncSession

from application.account.cqs.queries.load_dst import load_dst_account
from application.account.cqs.queries.load_src import load_src_account
from application.account.errors import AccountNotEnoughBalanceError
from application.account.schemas.model import (
    SchemaAccountTransferAmount,
    SchemaTransferRate,
)
from domain.account.events import AccountEvent
from domain.account.model import Account
from domain.vo.money import TransferRate
from shared.cqs.command import CommandBase
from shared.cqs.parser import auto_parse_kwargs


class TransferMoneyCommand(CommandBase):
    amount: SchemaAccountTransferAmount
    transfer_rate: SchemaTransferRate = TransferRate(1)


@load_src_account(for_update=True)
@load_dst_account(for_update=True)
@auto_parse_kwargs(command_type=TransferMoneyCommand)
async def handle(
    *,
    src_account: Account,
    dst_account: Account,
    db_session: AsyncSession,
    command: TransferMoneyCommand,
    **_,
) -> None:
    if src_account.balance < command.amount:
        raise AccountNotEnoughBalanceError

    db_session.add_all(
        AccountEvent.transfer_money(
            src_account=src_account,
            dst_account=dst_account,
            amount=command.amount,
            transfer_rate=command.transfer_rate,
        )
    )

    src_account.balance -= command.amount
    dst_account.balance += command.amount * command.transfer_rate

    await db_session.commit()
