from typing import Optional

from app.helpers.environment import env


class DatabaseSettings:
    type: str = env("DB_TYPE", "sqlite")
    driver: Optional[str] = env("DB_DRIVER")
    host: str = env("DB_HOST", "127.0.0.1")
    port: Optional[int] = env("DB_PORT")
    name: str = env("DB_NAME", "spartan")
    username: str = env("DB_USERNAME", "root")
    password: str = env("DB_PASSWORD", "root")
