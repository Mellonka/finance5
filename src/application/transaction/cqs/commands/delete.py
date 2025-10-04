from sqlalchemy.ext.asyncio import AsyncSession

from domain.transaction.model import Transaction


async def handle(*, transaction: Transaction, db_session: AsyncSession, **_) -> None:
    db_session.add(transaction)
    await db_session.delete(transaction)
    await db_session.commit()
