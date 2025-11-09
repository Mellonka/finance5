from shared.errors.base import BaseError


class ApplicationError(BaseError):
    message = 'Ошибка в приложении'


class AccessDeniedError(ApplicationError):
    message = 'Доступ к ресурсу запрещен'
