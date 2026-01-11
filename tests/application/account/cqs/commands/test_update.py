import pytest

from application.account.cqs.commands.update import (
    UpdateAccountBalanceCommand,
    UpdateAccountCodeCommand,
    UpdateAccountCurrencyCommand,
    UpdateAccountDescriptionCommand,
    UpdateAccountStatusCommand,
    UpdateAccountTagsCommand,
    UpdateAccountTypeCommand,
)
from application.account.cqs.commands.update import (
    auto_handle as update_handle,
)
from application.account.schemas.model import AccountSchema, SchemaCurrency
from domain.account.model import EnumAccountStatus, EnumAccountType
from domain.vo.money import Money
from shared.utils import uuid

commands = [
    UpdateAccountCodeCommand(code=uuid()),
    UpdateAccountDescriptionCommand(description=uuid()),
    UpdateAccountDescriptionCommand(description=None),
    *[UpdateAccountTypeCommand(type=type) for type in EnumAccountType],
    UpdateAccountTagsCommand(tags=[uuid()]),
    UpdateAccountBalanceCommand(balance=Money('69.69')),
    *[UpdateAccountCurrencyCommand(currency=SchemaCurrency(currency)) for currency in ['USD', 'EUR', 'RUB']],
    *[UpdateAccountStatusCommand(status=status) for status in EnumAccountStatus],
]


def check_updated_account(updated_account, command):
    match command:
        case UpdateAccountCodeCommand():
            assert updated_account.name == command.code
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


@pytest.mark.parametrize('use_auto', [True, False])
@pytest.mark.parametrize('command', commands)
async def test_handle_account_update(check_eq, dataset, session_maker, command, use_auto):
    """Тест обновления аккаунта в базе данных"""

    account = await dataset.account()

    async with session_maker() as db_session:
        if use_auto:
            updated_account = await update_handle(
                db_session=db_session,
                account=await dataset.load_account(account_id=account.id),
                **command.model_dump(),
            )
        else:
            updated_account = await update_handle(
                db_session=db_session,
                account=await dataset.load_account(account_id=account.id),
                commands=[command],
            )

    check_updated_account(updated_account, command)
    assert updated_account.updated > account.updated

    account = await dataset.load_account(account_id=account.id)
    check_eq(updated_account, account, schema=AccountSchema)


@pytest.mark.parametrize('use_auto', [True, False])
async def test_handle_account_update_commands(check_eq, dataset, session_maker, use_auto):
    """Тест обновления аккаунта в базе данных несколькими коммандами"""

    account = await dataset.account()

    name = uuid()
    description = uuid()
    tags = [uuid(), uuid()]
    balance = Money('69.69')
    commands = [
        UpdateAccountCodeCommand(code=name),
        UpdateAccountDescriptionCommand(description=description),
        UpdateAccountTagsCommand(tags=tags),
        UpdateAccountBalanceCommand(balance=balance),
    ]

    async with session_maker() as db_session:
        if use_auto:
            updated_account = await update_handle(
                db_session=db_session,
                account=await dataset.load_account(account_id=account.id),
                name=name,
                description=description,
                tags=tags,
                balance=balance,
            )
        else:
            updated_account = await update_handle(
                db_session=db_session,
                account=await dataset.load_account(account_id=account.id),
                commands=commands,
            )

    for command in commands:
        check_updated_account(updated_account, command)

    assert updated_account.updated > account.updated

    account = await dataset.load_account(account_id=account.id)
    check_eq(updated_account, account, schema=AccountSchema)
