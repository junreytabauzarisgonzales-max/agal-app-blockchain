class DomainError(Exception):
    status_code = 400


class DuplicateError(Exception):
    """An identical, actor-owned operation was already applied."""


class NotFoundError(DomainError):
    status_code = 404


class ForbiddenError(DomainError):
    status_code = 403


class ConflictError(DomainError):
    status_code = 409
