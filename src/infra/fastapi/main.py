from fastapi import FastAPI

from infra.fastapi.account import account_router

app = FastAPI()
app.include_router(account_router)
