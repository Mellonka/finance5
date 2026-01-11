from typing import Any


class BaseError(Exception):
    code = 'BASE_ERROR'
    message = 'Base error'
    details: dict[str, Any] | None = None

    def __init__(self, message: str | None = None, details: dict[str, Any] | None = None):
        if message is not None:
            self.message = message
        if details is not None:
            self.details = details

        super().__init__(self.message)

    def __str__(self) -> str:
        return f'{self.code}: {self.message}'

    def __repr__(self) -> str:
        return f'{self.code}: {self.message}'

    def to_dict(self) -> dict[str, Any]:
        return {'code': self.code, 'message': self.message, 'details': self.details}
