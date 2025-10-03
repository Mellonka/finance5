class DomainError(Exception):
    message = 'Базовая доменная ошибка'


class ConflictError(DomainError):
    message = 'Запись с таким ключом уже существует'


class NotFoundError(DomainError):
    message = 'Запись не найдена'
