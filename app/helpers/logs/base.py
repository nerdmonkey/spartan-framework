from abc import ABC, abstractmethod


class BaseLogger(ABC):
    """
    BaseLogger is an abstract base class that defines the interface for logging at various levels.
    Subclasses must implement all the methods to handle logging messages appropriately.

    Methods:
        debug(message, **kwargs):
            Log a message with debug level.
        info(message, **kwargs):
            Log a message with info level.
        warning(message, **kwargs):
            Log a message with warning level.
        error(message, **kwargs):
            Log a message with error level.
        critical(message, **kwargs):
            Log a message with critical level.
        exception(message, **kwargs):
            Log a message with exception level, typically used to log an error along with an exception traceback.
    """

    @abstractmethod
    def debug(self, message, **kwargs):
        pass

    @abstractmethod
    def info(self, message, **kwargs):
        pass

    @abstractmethod
    def warning(self, message, **kwargs):
        pass

    @abstractmethod
    def error(self, message, **kwargs):
        pass

    @abstractmethod
    def critical(self, message, **kwargs):
        pass

    @abstractmethod
    def exception(self, message, **kwargs):
        pass
