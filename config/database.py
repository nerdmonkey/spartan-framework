from typing import Union

from sqlalchemy import create_engine  # Import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session as SQLAlchemySession
from sqlalchemy.orm import sessionmaker

from config.app import get_settings


def create_database_engine() -> Engine:
    """
    Create and return the SQLAlchemy engine based on the database settings.

    The function reads the configuration from the environment, constructs the
    appropriate database URL, and creates an SQLAlchemy engine.

    Returns:
        Engine: An SQLAlchemy engine connected to the specified database.
    Raises:
        ValueError: If the database type is not supported.
    """
    settings = get_settings()
    database_type = settings.DB_TYPE
    database = settings.DB_NAME

    if database_type == "sqlite":
        database_url = f"sqlite:///./database/{database}.db"
        return create_engine(database_url, connect_args={"check_same_thread": False})

    # Mapping for different database types to their URL formats
    url_formats = {
        "psql": "postgresql+pg8000://{username}:{password}@{host}:{port}/{database}",
        "mysql": "mysql+pymysql://{username}:{password}@{host}:{port}/{database}",
    }

    if database_type in url_formats:
        database_url = url_formats[database_type].format(
            username=settings.DB_USERNAME,
            password=settings.DB_PASSWORD,
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            database=database,
        )
        return create_engine(database_url)

    raise ValueError(f"Unsupported database type: {database_type}")


engine = create_database_engine()
Session = sessionmaker(bind=engine)


def get_session() -> SQLAlchemySession:
    """
    Get a new SQLAlchemy session.

    Returns:
        SQLAlchemySession: A new SQLAlchemy session object.
    """
    return Session()
