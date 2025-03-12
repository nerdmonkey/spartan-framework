from typing import Dict

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session as SQLAlchemySession
from sqlalchemy.orm import sessionmaker

from app.helpers.environment import env


def create_database_engine() -> Engine:
    settings = env()
    database_type = settings.DB_TYPE
    database = settings.DB_NAME

    if settings.DB_SSL_CA is None:
        mysql_url_format = (
            "mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
        )
    else:
        mysql_url_format = (
            "mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
            "?ssl_ca={ssl_ca}&ssl_verify_cert={ssl_verify_cert}"
        )

    # Mapping for different database types to their URL formats
    url_formats: Dict[str, str] = {
        "sqlite": f"sqlite:///./database/{database}.db",
        "psql": "postgresql+pg8000://{username}:{password}@{host}:{port}/{database}",
        "mssql": "mssql+pyodbc://{username}:{password}@{host}:{port}/{database}?driver={driver}",
        "mysql": mysql_url_format,
    }

    if database_type in url_formats:
        database_url = url_formats[database_type]
        if database_type != "sqlite":
            database_url = database_url.format(
                username=settings.DB_USERNAME,
                password=settings.DB_PASSWORD,
                host=settings.DB_HOST,
                port=settings.DB_PORT,
                database=database,
                driver=settings.DB_DRIVER,
                ssl_ca=settings.DB_SSL_CA,
                ssl_verify_cert=settings.DB_SSL_VERIFY_CERT,
            )
        return create_engine(
            database_url,
            pool_size=30,  # Adjust pool size
            max_overflow=20,  # Adjust max overflow
            pool_timeout=30,  # Adjust pool timeout
            connect_args=(
                {"check_same_thread": False}
                if database_type == "sqlite"
                else {}
            ),
        )

    raise ValueError(f"Unsupported database type: {database_type}")


engine = create_database_engine()
Session = sessionmaker(bind=engine)


def db() -> SQLAlchemySession:
    return Session()
