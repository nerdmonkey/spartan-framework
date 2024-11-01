import json
from logging import FileHandler
from logging.handlers import SocketHandler

from aws_lambda_powertools.logging import Logger
from aws_lambda_powertools.logging.formatter import LambdaPowertoolsFormatter

from config.app import get_settings

settings = get_settings()

APP_NAME = settings.APP_NAME.lower()
LOG_LEVEL = settings.LOG_LEVEL
LOG_FILE = settings.LOG_FILE
LOG_CHANNEL = settings.LOG_CHANNEL
APP_ENVIRONMENT = settings.APP_ENVIRONMENT.lower()
TCP_LOG_HOST = "localhost"
TCP_LOG_PORT = 9999


class StandardLogFormatter(LambdaPowertoolsFormatter):
    def format(self, record):
        return super().format(record)


class FileLogFormatter(LambdaPowertoolsFormatter):
    def format(self, record):
        return super().format(record)


class ParseSocketHandler(SocketHandler):
    def makePickle(self, record):
        log_entry = json.loads(self.format(record))
        return (json.dumps(log_entry) + "\n").encode("utf-8")


class StandardLoggerService:
    def __init__(self):
        try:
            if APP_ENVIRONMENT in ["local"] and LOG_CHANNEL == "file":
                self.logger = Logger(
                    service=APP_NAME,
                    level=LOG_LEVEL,
                    formatter=FileLogFormatter(),
                    logger_handler=FileHandler(LOG_FILE),
                    json_deserializer=json.loads,
                )

            elif APP_ENVIRONMENT in ["local"] and LOG_CHANNEL == "server":
                tcp_handler = ParseSocketHandler(TCP_LOG_HOST, TCP_LOG_PORT)
                self.logger = Logger(
                    service=APP_NAME,
                    level=LOG_LEVEL,
                    formatter=StandardLogFormatter(),
                    logger_handler=tcp_handler,
                    json_deserializer=json.loads,
                )
            else:
                self.logger = Logger(
                    service=APP_NAME, level=LOG_LEVEL, formatter=StandardLogFormatter()
                )
        except Exception as e:
            self.logger = Logger(
                service=APP_NAME, level=LOG_LEVEL, formatter=StandardLogFormatter()
            )

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
