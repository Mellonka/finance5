from application.account.cqs.queries.list import (
    AccountStatusQuery,
    AccountTagsQuery,
    AccountTypeQuery,
)
from domain.account.model import EnumAccountStatus, EnumAccountType


type_queries = [
    AccountTypeQuery(type=[EnumAccountType.MONEY]),
    AccountTypeQuery(type=[EnumAccountType.LOAN, EnumAccountType.GOAL]),
    AccountTypeQuery(type=[EnumAccountType.MONEY, EnumAccountType.INVESTMENT]),
    AccountTypeQuery(type=list(EnumAccountType)),
    AccountTypeQuery(type=EnumAccountType.MONEY),
    AccountTypeQuery(type=EnumAccountType.LOAN),
    AccountTypeQuery(type=EnumAccountType.GOAL),
    AccountTypeQuery(type=[]),
]
status_queries = [
    AccountStatusQuery(status=EnumAccountStatus.ACTIVE),
    AccountStatusQuery(status=EnumAccountStatus.DISABLED),
]
tags_queries = [AccountTagsQuery(tags=[])]


async def test_list(check_eq, uuid, dataset, session_maker):
    tags = [
        (uuid(), uuid()),
        (uuid(), uuid()),
        (uuid(), uuid()),
    ]
    [
        await dataset.account(type=type, status=status, tags=[tag1, tag2])
        for type in EnumAccountType
        for status in EnumAccountStatus
        for tag1, tag2 in tags
    ]
