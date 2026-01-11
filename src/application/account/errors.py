from shared.errors.application import ApplicationError, IntegrityError, NotFoundError


class AccountNotFoundError(NotFoundError):
    code = 'ACCOUNT_NOT_FOUND_ERROR'
    message = 'Account not found'


class AccountIntegrityError(IntegrityError):
    code = 'ACCOUNT_INTEGRITY_ERROR'
    message = 'Account integrity violation'


class AccountNotEnoughBalanceError(ApplicationError):
    code = 'ACCOUNT_NOT_ENOUGH_BALANCE_ERROR'
    message = 'Account balance is not enough to perform the operation'
