from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from application.user.cqs.queries.load import auto_handle as load_handle
from application.user.schemas.model import SchemaUserDescription, SchemaUserName, SchemaUserStatus, SchemaUserTags
from domain.user.model import User
from shared.cqs.command import CommandBase
from shared.cqs.parser import auto_parse_kwargs
from shared.errors import ConflictError


class CreateUserCommand(CommandBase):
    name: SchemaUserName
    description: SchemaUserDescription
    status: SchemaUserStatus
    tags: SchemaUserTags


async def handle(*, db_session: AsyncSession, command: CreateUserCommand | None = None, **_) -> User:
    if not command:
        raise ValueError('Command must not be None')

    if await load_handle(db_session=db_session, name=command.name):
        raise ConflictError('A user with that name already exists')

    user = User(
        name=command.name,
        description=command.description,
        status=command.status,
        tags=command.tags,
    )
    db_session.add(user)
    await db_session.commit()

    return user


@auto_parse_kwargs(command_type=CreateUserCommand)
async def auto_handle(**kwargs: Any) -> User:
    return await handle(**kwargs)
