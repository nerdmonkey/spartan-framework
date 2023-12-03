from faker import Faker

from app.models.user import User
from config.database import get_session


def run():
    db = get_session()
    fake = Faker()

    for x in range(0, 30):
        user = {
            "username": fake.user_name(),
            "email": fake.email(),
            "password": fake.password(),
        }
        user = User(**user)
        db.add(user)
        db.commit()
        db.refresh(user)
