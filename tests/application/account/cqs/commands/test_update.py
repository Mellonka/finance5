import pytest

from application.account.cqs.commands.update import (
    UpdateAccountBalanceCommand,
    UpdateAccountCurrencyCommand,
    UpdateAccountDescriptionCommand,
    UpdateAccountNameCommand,
    UpdateAccountTagsCommand,
    UpdateAccountTypeCommand,
)
from application.account.cqs.commands.update import (
    handle as update_handle,
)
from application.account.cqs.schemas.model import AccountSchema
from domain.account.model import EnumAccountType
from domain.vo.currency import Currency
from domain.vo.money import Money
from shared.utils import uuid

commands = [
    UpdateAccountNameCommand(name=uuid()),
    UpdateAccountDescriptionCommand(description=uuid()),
    UpdateAccountDescriptionCommand(description=None),
    *[UpdateAccountTypeCommand(type=type) for type in EnumAccountType],
    UpdateAccountTagsCommand(tags=[uuid()]),
    UpdateAccountBalanceCommand(balance=Money('69.69')),
    *[UpdateAccountCurrencyCommand(currency=Currency(currency)) for currency in ['USD', 'EUR', 'RUB']],
]


def check_updated_account(updated_account, command):
    match command:
        case UpdateAccountNameCommand():
            assert updated_account.name == command.name
        case UpdateAccountDescriptionCommand():
            assert updated_account.description == command.description
        case UpdateAccountTypeCommand():
            assert updated_account.type == command.type
        case UpdateAccountTagsCommand():
            assert updated_account.tags == command.tags
        case UpdateAccountBalanceCommand():
            assert updated_account.balance == command.balance
        case UpdateAccountCurrencyCommand():
            assert updated_account.currency == command.currency


@pytest.mark.parametrize('command', commands)
async def test_command_apply(dataset, command):
    """Тест изменения аккаунта по команде"""

    account = await dataset.account()
    updated_account = command.apply(account)

    check_updated_account(updated_account, command)
    assert updated_account is account, 'Модификация должна быть in-place'


@pytest.mark.parametrize('command', commands)
async def test_handle_account_update(check_eq, dataset, session_maker, command):
    """Тест обновления аккаунта в базе данных"""

    account = await dataset.account()

    async with session_maker() as db_session:
        updated_account = await update_handle(
            db_session=db_session,
            account=await dataset.load_account(account_id=account.id),
            commands=[command],
        )

    check_updated_account(updated_account, command)
    assert updated_account.updated > account.updated

    account = await dataset.load_account(account_id=account.id)
    check_eq(updated_account, account, schema=AccountSchema)
