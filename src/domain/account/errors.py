from shared.errors.model import DomainError


class NegativeBalanceError(DomainError):
    message = 'Balance cannot be negative'
