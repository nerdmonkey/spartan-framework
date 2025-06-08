from app.helpers.logger.factory import LoggerFactory


class StandardLoggerService:
    def __init__(self, service_name="default_service", log_level="INFO"):
        """
        Initializes the logger service using LoggerFactory.
        """
        self.logger = LoggerFactory.create_logger(service_name, level=log_level)

    def debug(self, message, **kwargs):
        """
        Logs a message with level DEBUG.
        """
        self.logger.debug(message, **kwargs)

    def info(self, message, **kwargs):
        """
        Logs a message with level INFO.
        """
        self.logger.info(message, **kwargs)

    def warning(self, message, **kwargs):
        """
        Logs a message with level WARNING.
        """
        self.logger.warning(message, **kwargs)

    def error(self, message, **kwargs):
        """
        Logs a message with level ERROR.
        """
        self.logger.error(message, **kwargs)

    def critical(self, message, **kwargs):
        """
        Logs a message with level CRITICAL.
        """
        self.logger.critical(message, **kwargs)

    def exception(self, message, **kwargs):
        """
        Logs an exception with level ERROR, including the stack trace.
        """
        self.logger.exception(message, **kwargs)

    def set_level(self, log_level):
        """
        Sets the log level for the logger at runtime.
        """
        self.logger.setLevel(log_level)

    def get_logger(self):
        """
        Returns the underlying logger instance.
        """
        return self.logger
