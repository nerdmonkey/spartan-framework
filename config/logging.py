import json

from pydantic import BaseModel, ConfigDict, field_validator

from config.app import env


class BaseHandlerConfig(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    class_: str
    formatter: str


class ConsoleHandlerConfig(BaseHandlerConfig):
    name: str
    level: str


class FileHandlerConfig(BaseHandlerConfig):
    name: str
    level: str
    path: str


class TcpHandlerConfig(BaseHandlerConfig):
    name: str
    level: str
    host: str
    port: int

    @field_validator("port")
    def port_must_be_valid(cls, v):
        if not (0 <= v <= 65535):
            raise ValueError("Port must be between 0 and 65535")
        return v


handlers = {
    "console": ConsoleHandlerConfig(
        class_="logging.StreamHandler",
        name=env().APP_NAME,
        level=env().LOG_LEVEL,
        formatter="json",
    ),
    "file": FileHandlerConfig(
        class_="logging.FileHandler",
        name=env().APP_NAME,
        level=env().LOG_LEVEL,
        formatter="json",
        path=env().LOG_FILE,
    ),
    "tcp": TcpHandlerConfig(
        class_="logging.handlers.SocketHandler",
        name=env().APP_NAME,
        level=env().LOG_LEVEL,
        host="localhost",
        port=9999,
        formatter="json",
    ),
}


class Handlers:
    def __init__(self, handlers):
        self.handlers = handlers

    def __getattr__(self, item):
        return self.handlers.get(item, None)


handlers = Handlers(
    {
        "console": ConsoleHandlerConfig(
            class_="logging.StreamHandler",
            formatter="json",
            name=env().APP_NAME,
            level=env().LOG_LEVEL,
        ),
        "file": FileHandlerConfig(
            class_="logging.FileHandler",
            name=env().APP_NAME,
            level=env().LOG_LEVEL,
            formatter="json",
            path=env().LOG_FILE,
            json_deserializer=json.loads,
        ),
        "tcp": TcpHandlerConfig(
            class_="logging.handlers.SocketHandler",
            name=env().APP_NAME,
            level=env().LOG_LEVEL,
            host="localhost",
            port=9999,
            formatter="json",
        ),
    }
)


def handler(handler_type):
    return handlers.__getattr__(handler_type)
