from shared.errors.base import BaseError


class DomainError(BaseError):
    code = 'DOMAIN_ERROR'
    message = 'Error in domain model'
