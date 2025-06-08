from .base import BaseLogger
from .file import FileLogger
from .stream import StreamLogger

class BothLogger(BaseLogger):
    def __init__(self, service_name: str, level: str = "INFO"):
        self.file_logger = FileLogger(service_name=service_name, level=level)
        self.stream_logger = StreamLogger(service_name=service_name, level=level)
        self.level = level
        self.service_name = service_name

    def log(self, message: str, level: str = None):
        self.file_logger.log(message, level)
        self.stream_logger.log(message, level)
