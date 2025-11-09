import pytest

from application.account.cqs.commands.create import CreateAccountCommand
from application.account.cqs.commands.create import auto_handle as create_handle
from application.account.schemas.model import AccountSchema
from domain.account.model import EnumAccountStatus
from domain.vo.money import Money
from shared.errors import ConflictError
from shared.utils import uuid


@pytest.mark.parametrize('use_auto', [True, False])
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
    dataset,
    check_eq,
    session_maker,
    use_auto,
    name,
    description,
    balance,
    expected_balance,
    currency,
    type,
    tags,
):
    """Тест создания аккаунта"""

    user = await dataset.user()

    async with session_maker() as db_session:
        if use_auto:
            created_account = await create_handle(
                cur_user=user,
                db_session=db_session,
                name=name,
                description=description,
                balance=balance,
                currency=currency,
                type=type,
                tags=tags,
            )
        else:
            created_account = await create_handle(
                cur_user=user,
                db_session=db_session,
                command=CreateAccountCommand(
                    name=name,
                    description=description,
                    balance=balance,
                    currency=currency,
                    type=type,
                    tags=tags,
                ),
            )

        assert created_account

    async with session_maker() as db_session:
        loaded_account = await dataset.load_account(name=name, user_id=user.id)
        assert loaded_account

    assert loaded_account.name == name
    assert loaded_account.description == description
    assert str(loaded_account.balance) == expected_balance
    assert loaded_account.balance == Money(expected_balance)
    assert loaded_account.currency == currency
    assert loaded_account.type == type
    assert loaded_account.tags == tags
    assert loaded_account.status == EnumAccountStatus.ACTIVE
    assert loaded_account.user_id == user.id

    check_eq(created_account, loaded_account, schema=AccountSchema)


async def test_create_default_account(dataset, session_maker):
    """Тест создания дефолтного аккаунта"""

    user = await dataset.user()

    async with session_maker() as db_session:
        await create_handle(cur_user=user, db_session=db_session, name='test_create_default_account')

    account = await dataset.load_account(user_id=user.id, name='test_create_default_account')

    assert account.name == 'test_create_default_account'
    assert account.description is None
    assert account.balance == 0
    assert account.currency == 'RUB'
    assert account.tags == []
    assert account.status == EnumAccountStatus.ACTIVE
    assert account.user_id == user.id


async def test_conflict_error(dataset, session_maker):
    """Тест конфликта при создании двух аккаунтов с одним именем"""

    user = await dataset.user()

    with pytest.raises(ConflictError):
        async with session_maker() as db_session:
            await create_handle(cur_user=user, db_session=db_session, name='test_conflict_error')
            await create_handle(cur_user=user, db_session=db_session, name='test_conflict_error')
