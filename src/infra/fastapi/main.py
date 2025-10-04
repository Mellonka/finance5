from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqladmin import Admin, ModelView

from sqlalchemy.ext.asyncio import create_async_engine
from domain.user.model import User
from wtforms import Form, StringField, DecimalField, SelectField
from wtforms.validators import InputRequired
from domain.account.model import Account, EnumAccountStatus, EnumAccountType
from domain.category.model import Category
from domain.transaction.model import Transaction
from domain.vo.money import Money

async_engine = create_async_engine('sqlite+aiosqlite:///temp/finance5.db', echo=False)


@asynccontextmanager
async def lifespan(_: FastAPI):
    async with async_engine.begin() as conn:
        await conn.run_sync(User.metadata.create_all)
        await conn.run_sync(Account.metadata.create_all)
        await conn.run_sync(Category.metadata.create_all)
        await conn.run_sync(Transaction.metadata.create_all)

    yield


app = FastAPI(lifespan=lifespan)
admin = Admin(app, async_engine)


class UserAdmin(ModelView, model=User):
    pass


class AccountForm(Form):
    name = StringField(validators=[InputRequired()])
    user_id = StringField(validators=[InputRequired()])
    description = StringField(default=None)
    tags = StringField(default='[]')
    type = SelectField(choices=list((v, v) for v in EnumAccountType))
    status = SelectField(choices=list((v, v) for v in EnumAccountStatus))

    balance = DecimalField(default=Money('0'))
    currency = StringField(default='RUB')


class AccountAdmin(ModelView, model=Account):
    form = AccountForm
    column_list = [Account.name, Account.balance, Account.currency]


class CategoryAdmin(ModelView, model=Category):
    name_plural = 'Categories'
    column_list = [Category.name, Category.parent]


class TransactionAdmin(ModelView, model=Transaction):
    column_list = [Transaction.date, Transaction.amount, Transaction.account, Transaction.category]


admin.add_view(UserAdmin)
admin.add_view(AccountAdmin)
admin.add_view(CategoryAdmin)
admin.add_view(TransactionAdmin)
