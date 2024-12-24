from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session as SQLAlchemySession
from sqlalchemy.orm import sessionmaker

from app.helpers.environment import env


def create_database_engine() -> Engine:
    """
    Creates and returns a SQLAlchemy Engine instance based on the database configuration
    specified in the environment variables.

    The function supports multiple database types including SQLite, PostgreSQL, MySQL, and MSSQL.
    It constructs the appropriate database URL based on the database type and other configuration
    parameters such as username, password, host, port, and driver.

    Returns:
        Engine: A SQLAlchemy Engine instance configured for the specified database.

    Raises:
        ValueError: If the specified database type is not supported.

    Environment Variables:
        DB_TYPE (str): The type of the database (e.g., 'sqlite', 'psql', 'mysql', 'mssql').
        DB_NAME (str): The name of the database.
        DB_USERNAME (str): The username for the database (not required for SQLite).
        DB_PASSWORD (str): The password for the database (not required for SQLite).
        DB_HOST (str): The host of the database (not required for SQLite).
        DB_PORT (str): The port of the database (not required for SQLite).
        DB_DRIVER (str): The driver for the database (only required for MSSQL).
    """
    database_type = env().DB_TYPE
    database = env().DB_NAME

    url_formats = {
        "sqlite": f"sqlite:///./database/{database}.db",
        "psql": "postgresql+pg8000://{username}:{password}@{host}:{port}/{database}",
        "mysql": "mysql+pymysql://{username}:{password}@{host}:{port}/{database}",
        "mssql": "mssql+pyodbc://{username}:{password}@{host}:{port}/{database}?driver={driver}",
    }

    if database_type in url_formats:
        database_url = url_formats[database_type]
        if database_type != "sqlite":
            database_url = database_url.format(
                username=env().DB_USERNAME,
                password=env().DB_PASSWORD,
                host=env().DB_HOST,
                port=env().DB_PORT,
                database=database,
                driver=env().DB_DRIVER,
            )
        return create_engine(
            database_url,
            # pool_size=30,
            # max_overflow=30,
            connect_args={"check_same_thread": False}
            if database_type == "sqlite"
            else {},
        )

    raise ValueError(f"Unsupported database type: {database_type}")


engine = create_database_engine()
Session = sessionmaker(bind=engine)


def db() -> SQLAlchemySession:
    """
    Creates and returns a new SQLAlchemy session.

    Returns:
        SQLAlchemySession: A new SQLAlchemy session instance.
    """
    return Session()
