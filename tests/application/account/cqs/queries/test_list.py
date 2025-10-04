from application.account.cqs.queries.list import (
    ListAccountStatusQuery,
    ListAccountTagsQuery,
    ListAccountTypeQuery,
)
from domain.account.model import EnumAccountStatus, EnumAccountType


type_queries = [
    ListAccountTypeQuery(type=[EnumAccountType.MONEY]),
    ListAccountTypeQuery(type=[EnumAccountType.LOAN, EnumAccountType.GOAL]),
    ListAccountTypeQuery(type=[EnumAccountType.MONEY, EnumAccountType.INVESTMENT]),
    ListAccountTypeQuery(type=list(EnumAccountType)),
    ListAccountTypeQuery(),
]
status_queries = [
    ListAccountStatusQuery(status=EnumAccountStatus.ACTIVE),
    ListAccountStatusQuery(status=EnumAccountStatus.DISABLED),
]
tags_queries = [ListAccountTagsQuery(tags=[])]


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
