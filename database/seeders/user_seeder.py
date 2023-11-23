from config.database import get_session
from app.models.user import User
from faker import Faker

def run():
    db = get_session()
    fake = Faker()

    for x in range(1,30):
        user = {
            "username": fake.user_name(),
            "email": fake.email(),
            "password": fake.password(),
        }
        user = User(**user)
        db.add(user)
        db.commit()
        db.refresh(user)
