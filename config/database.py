from config.app import get_settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


settings = get_settings()
database = settings.DB_NAME

if settings.DB_TYPE == "sqlite":
    database_url = f"sqlite:///./database/{database}.db"
    engine = create_engine(database_url, connect_args={"check_same_thread": False})
else:
    host = settings.DB_HOST
    port = settings.DB_PORT
    username = settings.DB_USERNAME
    password = settings.DB_PASSWORD
    database_type = settings.DB_TYPE

    if database_type == "psql":
        database_url = (
            f"postgresql+pg8000://{username}:{password}@{host}:{port}/{database}"
        )
    elif database_type == "mysql":
        database_url = (
            f"postgresql+pg8000://{username}:{password}@{host}:{port}/{database}"
        )
    else:
        database_url = (
            f"postgresql+pg8000://{username}:{password}@{host}:{port}/{database}"
        )
    engine = create_engine(database_url)


Session = sessionmaker(bind=engine)


def get_session() -> Session:
    return Session()
