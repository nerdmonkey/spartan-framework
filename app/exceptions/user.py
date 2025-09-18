class UserNotFoundException(Exception):
    def __init__(self, message="User not found"):
        self.message = message
        super().__init__(self.message)


class DuplicateUserError(Exception):
    """
    Exception raised when attempting to create a user that already exists.

    This error should be used to indicate that a user creation operation
    has failed due to the presence of a user with the same identifying
    information.

    Attributes:
        message (str): Explanation of the error.
    """


class InternalServerErrorException(Exception):
    def __init__(self, message="Internal server error"):
        self.message = message
        super().__init__(self.message)


class UnauthorizedException(Exception):
    def __init__(self, message="Unauthorized access"):
        self.message = message
        super().__init__(self.message)


class InvalidSortFieldException(Exception):
    def __init__(self, message="Invalid sort field"):
        self.message = message
        super().__init__(self.message)


class InvalidSortTypeException(Exception):
    def __init__(self, message="Invalid sort type"):
        self.message = message
        super().__init__(self.message)
