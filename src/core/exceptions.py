class NotFoundError(Exception): 
    """Resource not found."""

    pass


class DuplicateEntryError(Exception):
    """Duplicate entry."""

    pass


class AlreadyExistsError(Exception):
    """Resource already exists."""

    pass


class InvalidCredentialsError(Exception):
    """Invalid credentials."""

    pass


class TokenExpiredError(Exception):
    """Token has expired."""

    pass


class InvalidTokenError(Exception):
    """Invalid token."""

    pass


class InvalidRequestError(Exception):
    """Invalid request."""

    pass
