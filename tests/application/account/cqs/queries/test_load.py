from application.account.cqs.queries.load import LoadByAccountIDQuery, LoadByAccountNameQuery
from application.account.cqs.queries.load import handle as load_handle
from application.account.cqs.schemas.model import AccountSchema


async def test_load_account_by_name(check_eq, dataset, session_maker):
    """Тест загрузки аккаунта по имени"""

    account = await dataset.account()

    async with session_maker() as db_session:
        loaded_by_query = await load_handle(db_session=db_session, query=LoadByAccountNameQuery(name=account.name))
        assert loaded_by_query

    async with session_maker() as db_session:
        loaded_by_kwargs = await load_handle(db_session=db_session, name=account.name)
        assert loaded_by_kwargs

    check_eq(account, loaded_by_query, loaded_by_kwargs, schema=AccountSchema)


async def test_load_account_by_id(check_eq, dataset, session_maker):
    """Тест загрузки аккаунта по ID"""

    account = await dataset.account()

    async with session_maker() as db_session:
        loaded_by_query = await load_handle(db_session=db_session, query=LoadByAccountIDQuery(account_id=account.id))
        assert loaded_by_query

    async with session_maker() as db_session:
        loaded_by_kwargs = await load_handle(db_session=db_session, account_id=account.id)
        assert loaded_by_kwargs

    check_eq(account, loaded_by_query, loaded_by_kwargs, schema=AccountSchema)


async def test_load_absent_account(uuid, uuid7, session_maker):
    """Тест загрузки отсутствующего аккаунта"""

    name = uuid()
    account_id = uuid7()

    async with session_maker() as db_session:
        loaded = await load_handle(db_session=db_session, query=LoadByAccountNameQuery(name=name))
        assert loaded is None

        loaded = await load_handle(db_session=db_session, name=name)
        assert loaded is None

        loaded = await load_handle(db_session=db_session, query=LoadByAccountIDQuery(account_id=account_id))
        assert loaded is None

        loaded = await load_handle(db_session=db_session, account_id=account_id)
        assert loaded is None
