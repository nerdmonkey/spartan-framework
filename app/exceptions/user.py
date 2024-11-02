class UserNotFoundError(Exception):
    """Raised when a user is not found in the database."""

    pass


class DuplicateUserError(Exception):
    """Raised when attempting to create a user with an email that already exists."""

    pass


class InvalidSortFieldError(Exception):
    """Raised when an invalid field is used for sorting."""

    pass
