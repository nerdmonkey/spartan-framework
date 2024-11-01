from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session as SQLAlchemySession
from sqlalchemy.orm import sessionmaker

from config.app import env


def create_database_engine() -> Engine:
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
    return Session()
