import json

from aws_lambda_powertools.logging import Logger

from app.helpers.logs.base import BaseLogger
from app.helpers.logs.formatter.standard import StandardLogFormatter
from app.helpers.logs.formatter.tcp import TCPLogFormatter
from config.logging import handler


class TCPLogger(BaseLogger):
    def __init__(self):
        tcp_handler = TCPLogFormatter(handler.tcp.host, handler.tcp.port)
        self.logger = Logger(
            service=handler.tcp.name,
            level=handler.tcp.level,
            formatter=StandardLogFormatter(),
            logger_handler=tcp_handler,
            json_deserializer=json.loads,
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
