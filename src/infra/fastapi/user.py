from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from application.user.cqs.queries.load import auto_handle as user_load_handle
from infra.di.database import async_db_session


async def load_admin_user(db_session: AsyncSession = Depends(async_db_session)):
    cur_user = await user_load_handle(db_session=db_session, name='admin')
    if cur_user is None:
        raise HTTPException(404, 'User not found')
    return cur_user
