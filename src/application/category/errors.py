from shared.errors.application import IntegrityError, NotFoundError


class CategoryNotFoundError(NotFoundError):
    code = 'CATEGORY_NOT_FOUND_ERROR'
    message = 'Category not found'


class CategoryIntegrityError(IntegrityError):
    code = 'CATEGORY_INTEGRITY_ERROR'
    message = 'Category integrity violation'
