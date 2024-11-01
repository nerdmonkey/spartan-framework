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
            if env().APP_ENVIRONMENT in ["local"] and env().LOG_CHANNEL == "file":
                self.logger = Logger(
                    service=handler.file.name,
                    level=handler.file.level,
                    formatter=FileLogFormatter(),
                    logger_handler=FileHandler(handler.file.path),
                    json_deserializer=handler.file.json_deserializer,
                )

            elif env().APP_ENVIRONMENT in ["local"] and env().LOG_CHANNEL == "tcp":
                tcp_handler = ParseSocketHandler(handler.tcp.host, handler.tcp.port)
                self.logger = Logger(
                    service=handler.tcp.name,
                    level=handler.tcp.level,
                    formatter=StandardLogFormatter(),
                    logger_handler=tcp_handler,
                    json_deserializer=json.loads,
                )
            else:
                self.logger = Logger(
                    service=env().APP_NAME,
                    level=env().LOG_LEVEL,
                    formatter=StandardLogFormatter(),
                )
        except Exception as e:
            self.logger = Logger(
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
