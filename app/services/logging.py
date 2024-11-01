import json
from logging import FileHandler
from logging.handlers import SocketHandler

from aws_lambda_powertools.logging import Logger
from aws_lambda_powertools.logging.formatter import LambdaPowertoolsFormatter

from config.app import env
from config.logging import handler


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
        return Logger(
            service=handler.file.name,
            level=handler.file.level,
            formatter=FileLogFormatter(),
            logger_handler=FileHandler(handler.file.path),
            json_deserializer=handler.file.json_deserializer,
        )

    def _create_tcp_logger(self):
        tcp_handler = ParseSocketHandler(handler.tcp.host, handler.tcp.port)
        return Logger(
            service=handler.tcp.name,
            level=handler.tcp.level,
            formatter=StandardLogFormatter(),
            logger_handler=tcp_handler,
            json_deserializer=json.loads,
        )

    def _create_default_logger(self):
        return Logger(
            service=env().APP_NAME,
            level=env().LOG_LEVEL,
            formatter=StandardLogFormatter(),
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
