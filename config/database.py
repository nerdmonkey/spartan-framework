import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

database = os.environ.get("DB_NAME")

if os.environ.get("DB_TYPE") == "sqlite":
    database_url = f"sqlite:///./database/{database}.db"
    engine = create_engine(database_url, connect_args={"check_same_thread": False})
else:
    host = os.environ.get("DB_HOST")
    port = os.environ.get("DB_PORT")
    username = os.environ.get("DB_USERNAME")
    password = os.environ.get("DB_PASSWORD")
    database_type = os.environ.get("DB_TYPE")

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
