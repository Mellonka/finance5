from sqlalchemy import select

from application.account.cqs.queries.load import AccountsIsolateByUser
from domain.account.model import Account, EnumAccountStatus
from shared.cqs.generator import generate_list_handle

handle = generate_list_handle(
    base_statement=select(Account).where(Account.status == EnumAccountStatus.DISABLED).order_by(Account.id),
    query_types=[
        AccountsIsolateByUser,  # Изолируем по пользователю если пробросили cur_user
    ],
)
