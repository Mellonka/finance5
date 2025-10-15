from collections import defaultdict
import datetime as dt

from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from application.account.schemas.model import SchemaAccountID
from application.category.schemas.model import SchemaCategoryID
from application.transaction.cqs.queries.list import ListTransactionQuery
from application.transaction.cqs.queries.load import load_query_parse
from domain.transaction.model import EnumTransactionType, Transaction
from domain.vo.money import Money
from shared.cqs.query.handler import QueryHandlerABC


class AnalyticsByDay(BaseModel):
    date: dt.date
    by_accounts: dict[SchemaAccountID, Money] = Field(default_factory=lambda: defaultdict(Money))
    by_categories: dict[SchemaCategoryID, Money] = Field(default_factory=lambda: defaultdict(Money))


class Analytics(BaseModel):
    income: list[AnalyticsByDay]
    expense: list[AnalyticsByDay]


class AnalyticsHandler(QueryHandlerABC):
    async def handle(self, *, db_session: AsyncSession, queries: list[ListTransactionQuery], **_) -> Analytics:
        transactions_stream = await db_session.stream(
            self.render_statement(
                queries,  # pyright: ignore[reportArgumentType]
                select(
                    Transaction.date,
                    Transaction.type,
                    Transaction.amount,
                    Transaction.account_id,
                    Transaction.category_id,
                ),
            ).order_by(Transaction.date)
        )

        income_analytics = []
        expense_analytics = []

        async for date, type, amount, account_id, category_id in transactions_stream:
            analytics = expense_analytics
            if type == EnumTransactionType.INCOME:
                analytics = income_analytics

            if not analytics or analytics[-1].date != date:
                analytics.append(AnalyticsByDay(date=date))

            analytics[-1].by_accounts[account_id] += amount
            analytics[-1].by_categories[category_id] += amount

        return Analytics(income=income_analytics, expense=expense_analytics)


handler = AnalyticsHandler(Transaction, load_query_parse)
