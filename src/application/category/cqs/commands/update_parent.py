import sqlalchemy.exc
from sqlalchemy.ext.asyncio import AsyncSession

from application.category.cqs.queries.load import load_category
from application.category.errors import CategoryIntegrityError, CategoryNotFoundError
from application.category.schemas.model import SchemaCategoryID
from application.category.storage.advisory_lock import with_lock_all_user_categories
from application.category.storage.repository import CategoryRepository, make_category_repo
from domain.category.model import Category
from domain.user.model import User
from shared.cqs.command import CommandBase


class UpdateCategoryParentCommand(CommandBase):
    parent_id: SchemaCategoryID


@make_category_repo
@load_category(for_update=True)
@with_lock_all_user_categories
# ^
# Появится циклическая зависимость если конкуретно поменять родителя
# и у родителя нового родителя поменять родителя на текущую категорию.
# Не понятно как такое решать, пока как решение в голову приходит только
# заблокировать все категории пользователя для этой оперции.
# Обязательно должно быть
async def handle(
    *,
    cur_user: User,
    category: Category,
    db_session: AsyncSession,
    category_repo: CategoryRepository,
    command: UpdateCategoryParentCommand,
    **_,
) -> Category:
    if category.id == command.parent_id:
        raise CategoryIntegrityError('Category cannot be a parent for itself')

    parent_category = await category_repo.load_by(category_id=command.parent_id, user_id=cur_user.id)

    if not parent_category:
        raise CategoryNotFoundError('Parent category not found')

    while parent_category and parent_category.parent_id and parent_category.parent_id != category.id:
        parent_category = await category_repo.load_by(category_id=parent_category.parent_id, user_id=cur_user.id)

    if parent_category and parent_category.parent_id == category.id:
        raise CategoryIntegrityError('Cyclic hierarchies of categories are not allowed')

    category.parent_id = command.parent_id

    try:
        await db_session.commit()
    except sqlalchemy.exc.IntegrityError as exc:
        raise CategoryIntegrityError from exc

    return category
