from uuid import UUID
from sqlalchemy import Select
from domain.account.model import Account
from shared.storage.repository import RepositoryBase, RepositoryConfig
from shared.storage.filters import FilterHandler, UseInForArrays


class AccountUseInForArrays(UseInForArrays):
    whitelist = {Account.tags}


class AccountFilterHandler(FilterHandler[Account]):
    @classmethod
    def account_id(
        cls, entity_cls: type[Account], statement: Select[tuple[Account]], value: list[UUID] | UUID
    ) -> Select[tuple[Account]]:
        if isinstance(value, (list, tuple)):
            return statement.where(Account.id.in_(value))
        return statement.where(Account.id == value)


class AccountRepository(
    RepositoryBase,
    config=RepositoryConfig(
        entity_cls=Account,
        primary_key=Account.id,
        filter_handlers=[AccountUseInForArrays, AccountFilterHandler],
    ),
):
    pass
