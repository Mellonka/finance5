from shared.errors.base import BaseError


class DomainError(BaseError):
    message = 'Ошибка в домене'


class ConflictError(DomainError):
    message = 'Запись с таким ключом уже существует'


class NotFoundError(DomainError):
    message = 'Запись не найдена'
