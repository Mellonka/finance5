from shared.errors.base import BaseError


class ApplicationError(BaseError):
    code = 'APPLICATION_ERROR'
    message = 'Error in application logic'


class AccessDeniedError(ApplicationError):
    code = 'ACCESS_DENIED_ERROR'
    message = 'Access to resource denied'


class IntegrityError(ApplicationError):
    code = 'INTEGRITY_ERROR'
    message = 'Violation of the integrity'


class NotFoundError(ApplicationError):
    code = 'NOT_FOUND_ERROR'
    message = 'Resource not found'
