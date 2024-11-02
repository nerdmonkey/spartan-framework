class DatabaseInternalError(Exception):
    """
    Exception raised for internal errors in the database operations.

    This exception is intended to be used when an unexpected error occurs
    within the database layer that does not fall under more specific
    database-related exceptions.

    Attributes:
        message (str): Explanation of the error.
    """

    pass
