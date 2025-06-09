import json

from .base import BaseLogger
from .file import FileLogger
from .stream import StreamLogger


def _prettify_extra(extra):
    if not extra:
        return ""
    try:
        return f" | extra: {json.dumps(extra, ensure_ascii=False)}"
    except Exception:
        return f" | extra: {str(extra)}"


class BothLogger(BaseLogger):
    def __init__(self, service_name: str, level: str = "INFO"):
        self.file_logger = FileLogger(service_name=service_name, level=level)
        self.stream_logger = StreamLogger(
            service_name=service_name, level=level
        )
        self.level = level
        self.service_name = service_name

    def log(self, message: str, level: str = None):
        self.file_logger.log(message, level)
        self.stream_logger.log(message, level)

    def info(self, message: str, **kwargs):
        extra = kwargs.get("extra")
        stacklevel = kwargs.pop("stacklevel", 6)  # Set higher default
        self.file_logger.info(message, **{**kwargs, "stacklevel": stacklevel})
        self.stream_logger.info(message + _prettify_extra(extra))

    def warning(self, message: str, **kwargs):
        extra = kwargs.get("extra")
        stacklevel = kwargs.pop("stacklevel", 6)
        self.file_logger.warning(message, **{**kwargs, "stacklevel": stacklevel})
        self.stream_logger.warning(message + _prettify_extra(extra))

    def error(self, message: str, **kwargs):
        extra = kwargs.get("extra")
        stacklevel = kwargs.pop("stacklevel", 6)
        self.file_logger.error(message, **{**kwargs, "stacklevel": stacklevel})
        self.stream_logger.error(message + _prettify_extra(extra))

    def debug(self, message: str, **kwargs):
        extra = kwargs.get("extra")
        stacklevel = kwargs.pop("stacklevel", 6)
        self.file_logger.debug(message, **{**kwargs, "stacklevel": stacklevel})
        self.stream_logger.debug(message + _prettify_extra(extra))

    def exception(self, message: str, *args, **kwargs):
        extra = kwargs.get("extra")
        stacklevel = kwargs.pop("stacklevel", 6)
        self.file_logger.exception(message, *args, **{**kwargs, "stacklevel": stacklevel})
        self.stream_logger.exception(message, extra=extra)
