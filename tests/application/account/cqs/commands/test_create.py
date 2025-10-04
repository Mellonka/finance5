import pytest
from sqlalchemy import select

from application.account.cqs.commands.create import CreateAccountCommand
from application.account.cqs.commands.create import handle as create_handle
from application.account.schemas.model import AccountSchema
from domain.account.model import Account, EnumAccountStatus
from domain.vo.money import Money
from shared.errors.model import ConflictError
from shared.utils import uuid


@pytest.mark.parametrize(
    'name,description,balance,expected_balance,currency,type,tags',
    [
        [uuid(), uuid(), '69.69', '69.69000', 'USD', 'MONEY', []],
        [uuid(), None, '69.6969', '69.69690', 'RUB', 'GOAL', ['some_tag']],
        [uuid(), uuid(), '99.696961', '99.69696', 'USD', 'MONEY', []],
        [uuid(), uuid(), '99.696967', '99.69697', 'USD', 'MONEY', []],
    ],
)
async def test_create_account(
    uuid7, check_eq, session_maker, name, description, balance, expected_balance, currency, type, tags
):
    """Тест создания аккаунта"""

    command = CreateAccountCommand(
        name=name,
        description=description,
        balance=balance,
        currency=currency,
        type=type,
        tags=tags,
        user_id=(user_id := uuid7()),
    )

    async with session_maker() as db_session:
        created_account = await create_handle(db_session=db_session, command=command)
        assert created_account

    async with session_maker() as db_session:
        loaded_account = await db_session.scalar(
            select(Account).where(Account.name == name, Account.user_id == user_id)
        )
        assert loaded_account

    check_eq(created_account, loaded_account, schema=AccountSchema)

    assert loaded_account.name == name
    assert loaded_account.description == description
    assert str(loaded_account.balance) == expected_balance
    assert loaded_account.balance == Money(expected_balance)
    assert loaded_account.currency == currency
    assert loaded_account.type == type
    assert loaded_account.tags == tags
    assert loaded_account.status == EnumAccountStatus.ACTIVE
    assert loaded_account.user_id == user_id


async def test_conflict_error(session_maker, uuid7):
    """Тест конфликта при создании двух аккаунтов с одним именем"""

    with pytest.raises(ConflictError):
        command = CreateAccountCommand.model_validate({'user_id': uuid7(), 'name': uuid()})
        async with session_maker() as db_session:
            await create_handle(db_session=db_session, command=command)
            await create_handle(db_session=db_session, command=command)
