import json
from logging import FileHandler
from logging.handlers import SocketHandler

from aws_lambda_powertools.logging import Logger
from aws_lambda_powertools.logging.formatter import LambdaPowertoolsFormatter

from config.app import env
from config.logging import handler


class StandardLogFormatter(LambdaPowertoolsFormatter):
    """
    StandardLogFormatter class that extends LambdaPowertoolsFormatter.

    This class provides a custom log formatter for the application. It overrides
    the `format` method to use the parent class's formatting functionality.

    Methods:
        format(record): Formats the specified log record as text.

    Args:
        record (logging.LogRecord): The log record to be formatted.

    Returns:
        str: The formatted log record as a string.
    """
    def format(self, record):
        return super().format(record)


class FileLogFormatter(LambdaPowertoolsFormatter):
    """
    A custom log formatter that extends the LambdaPowertoolsFormatter.

    This formatter is used to format log records for file logging.

    Methods:
        format(record): Formats the specified log record as text.
    """
    def format(self, record):
        return super().format(record)


class ParseSocketHandler(SocketHandler):
    """
    A custom logging handler that extends SocketHandler to format log records
    as JSON strings before sending them over a socket.

    Methods:
        makePickle(record):
            Converts a log record to a JSON string, encodes it in UTF-8, and
            returns the byte representation.
    """
    def makePickle(self, record):
        log_entry = json.loads(self.format(record))
        return (json.dumps(log_entry) + "\n").encode("utf-8")


class StandardLoggerService:
    """
    StandardLoggerService is responsible for creating and managing different types of loggers
    based on the application environment and logging channel configuration.

    Methods
    -------
    __init__():
        Initializes the logger based on the environment and logging channel.

    _create_file_logger():
        Creates and returns a file-based logger.

    _create_tcp_logger():
        Creates and returns a TCP-based logger.

    _create_default_logger():
        Creates and returns a default logger.

    debug(message, **kwargs):
        Logs a message with level DEBUG.

    info(message, **kwargs):
        Logs a message with level INFO.

    warning(message, **kwargs):
        Logs a message with level WARNING.

    error(message, **kwargs):
        Logs a message with level ERROR.

    critical(message, **kwargs):
        Logs a message with level CRITICAL.

    exception(message, **kwargs):
        Logs a message with level ERROR, including exception information.
    """

    def __init__(self):
        """
        Initializes the logger based on the application environment and log channel.

        The logger is created based on the following conditions:
        - If the application environment is "local" and the log channel is "file", a file logger is created.
        - If the application environment is "local" and the log channel is "tcp", a TCP logger is created.
        - For any other conditions, a default logger is created.

        If an exception occurs during initialization, a default logger is created.

        Attributes:
            logger: The logger instance created based on the conditions.
        """
        try:
            app_env = env().APP_ENVIRONMENT
            log_channel = env().LOG_CHANNEL
            if app_env == "local" and log_channel == "file":
                self.logger = self._create_file_logger()
            elif app_env == "local" and log_channel == "tcp":
                self.logger = self._create_tcp_logger()
            else:
                self.logger = self._create_default_logger()
        except Exception:
            self.logger = self._create_default_logger()

    def _create_file_logger(self):
        """
        Creates a file logger instance.

        This method initializes and returns a Logger object configured to log messages to a file.

        Returns:
            Logger: A logger instance configured with a file handler.
        """
        return Logger(
            service=handler.file.name,
            level=handler.file.level,
            formatter=FileLogFormatter(),
            logger_handler=FileHandler(handler.file.path),
            json_deserializer=handler.file.json_deserializer,
        )

    def _create_tcp_logger(self):
        """
        Creates a TCP logger instance.

        This method initializes a TCP logger using the provided handler's TCP
        configuration. It sets up the logger with a specific service name, log
        level, formatter, and handler.

        Returns:
            Logger: A configured Logger instance with a TCP handler.
        """
        tcp_handler = ParseSocketHandler(handler.tcp.host, handler.tcp.port)
        return Logger(
            service=handler.tcp.name,
            level=handler.tcp.level,
            formatter=StandardLogFormatter(),
            logger_handler=tcp_handler,
            json_deserializer=json.loads,
        )

    def _create_default_logger(self):
        """
        Creates and returns a default logger instance.

        This logger is configured with the application's name, log level, and a standard log formatter.

        Returns:
            Logger: A configured logger instance.
        """
        return Logger(
            service=env().APP_NAME,
            level=env().LOG_LEVEL,
            formatter=StandardLogFormatter(),
        )

    def debug(self, message, **kwargs):
        """
        Logs a debug message.

        Args:
            message (str): The debug message to log.
            **kwargs: Additional keyword arguments to pass to the logger.

        Returns:
            None
        """
        self.logger.debug(message, **kwargs)

    def info(self, message, **kwargs):
        """
        Logs an informational message.

        Parameters:
            message (str): The message to log.
            **kwargs: Additional keyword arguments to pass to the logger.
        """
        self.logger.info(message, **kwargs)

    def warning(self, message, **kwargs):
        """
        Logs a warning message.

        Args:
            message (str): The warning message to log.
            **kwargs: Additional keyword arguments to pass to the logger.
        """
        self.logger.warning(message, **kwargs)

    def error(self, message, **kwargs):
        """
        Logs an error message.

        Args:
            message (str): The error message to log.
            **kwargs: Additional keyword arguments to pass to the logger.
        """
        self.logger.error(message, **kwargs)

    def critical(self, message, **kwargs):
        """
        Logs a critical message.

        Args:
            message (str): The critical message to log.
            **kwargs: Additional keyword arguments to pass to the logger.

        Returns:
            None
        """
        self.logger.critical(message, **kwargs)

    def exception(self, message, **kwargs):
        """
        Logs a message with level ERROR on this logger. The arguments are interpreted as for debug().

        Args:
            message (str): The message to be logged.
            **kwargs: Additional keyword arguments to pass to the logger.

        Returns:
            None
        """
        self.logger.exception(message, **kwargs)
