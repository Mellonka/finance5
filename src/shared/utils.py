import datetime as dt

import uuid_utils
from uuid_utils.compat import uuid7  # noqa: F401


def uuid() -> str:
    return uuid_utils.uuid7().hex


def now(tz=dt.UTC) -> dt.datetime:
    return dt.datetime.now(tz)
