class UserNotFoundError(Exception):
    """
    Exception raised when a user is not found in the system.

    This exception should be used to indicate that a requested user could not be located,
    typically in scenarios where user data is being queried or accessed.

    Attributes:
        message (str): Explanation of the error.
    """


class DuplicateUserError(Exception):
    """
    Exception raised when attempting to create a user that already exists.

    This error should be used to indicate that a user creation operation
    has failed due to the presence of a user with the same identifying
    information.

    Attributes:
        message (str): Explanation of the error.
    """


class InvalidSortFieldError(Exception):
    """
    Exception raised for errors in the sorting field.

    Attributes:
        message -- explanation of the error
    """
