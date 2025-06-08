from app.helpers.environment import env


class LogSettings:
    level: str = env("LOG_LEVEL", "DEBUG")
    dir: str = env("LOG_DIR", "storage/logs")
    channel: str = env("LOG_CHANNEL", "file")
