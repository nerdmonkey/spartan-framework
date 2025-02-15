from app.helpers.logger.factory import LoggerFactory


class StandardLoggerService:
    def __init__(self, service_name="default_service", log_level="INFO"):
        """
        Initializes the logger service using LoggerFactory.
        """
        self.logger = LoggerFactory.create_logger(service_name, level=log_level)

    def debug(self, message, **kwargs):
        self.logger.debug(message, **kwargs)

    def info(self, message, **kwargs):
        self.logger.info(message, **kwargs)

    def warning(self, message, **kwargs):
        self.logger.warning(message, **kwargs)

    def error(self, message, **kwargs):
        self.logger.error(message, **kwargs)

    def critical(self, message, **kwargs):
        self.logger.critical(message, **kwargs)

    def exception(self, message, **kwargs):
        self.logger.exception(message, **kwargs)
