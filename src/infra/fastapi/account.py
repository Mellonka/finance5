from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from application.account.schemas.model import AccountSchema
from application.account.cqs.commands.create import handle as account_create_command
from application.account.cqs.commands.create import CreateAccountCommand
from domain.user.model import User
from infra.di.database import async_db_session
from infra.fastapi.user import load_admin_user

account_router = APIRouter(prefix='/accounts', tags=['accounts'])


@account_router.post('/')
async def create_account(
    command: CreateAccountCommand,
    db_session: AsyncSession = Depends(async_db_session),
    cur_user: User = Depends(load_admin_user),
) -> AccountSchema:
    account = await account_create_command(
        cur_user=cur_user,
        db_session=db_session,
        command=command,
    )
    return AccountSchema.model_validate(account)
