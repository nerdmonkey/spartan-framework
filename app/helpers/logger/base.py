from abc import ABC, abstractmethod


class BaseLogger(ABC):
    @abstractmethod
    def info(self, message: str, **kwargs):
        pass

    @abstractmethod
    def error(self, message: str, **kwargs):
        pass

    @abstractmethod
    def warning(self, message: str, **kwargs):
        pass

    @abstractmethod
    def debug(self, message: str, **kwargs):
        pass

    @abstractmethod
    def exception(self, message: str, **kwargs):
        pass
