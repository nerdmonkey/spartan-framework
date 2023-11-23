from config.database import get_session
from app.models.user import User

def run():
    users = [
        {
            "username": "andeng",
            "email": "andeng@python-spartan.com",
            "password": "andeng",
        },
        {
            "username": "iviang",
            "email": "iviang@python-spartan.com",
            "password": "iviang",
        },
        {"username": "loki", "email": "loki@python-spartan.com", "password": "loki"},
        {"username": "laleng", "email": "laleng@python-spartan.com", "password": "laleng"},
        {"username": "zeus", "email": "zeus@python-spartan.com", "password": "zeus123"},
        {"username": "hera", "email": "hera@python-spartan.com", "password": "hera123"},
        {
            "username": "athena",
            "email": "athena@python-spartan.com",
            "password": "athena123",
        },
        {
            "username": "apollo",
            "email": "apollo@python-spartan.com",
            "password": "apollo123",
        },
        {
            "username": "artemis",
            "email": "artemis@python-spartan.com",
            "password": "artemis123",
        },
        {
            "username": "hunk",
            "email": "hunk@python-spartan.com",
            "password": "hunk123",
        },
    ]

    user_model = User
    db = get_session()

    for user in users:
        user = User(username=user['username'], email=user['email'], password=user['password'])
        db.add(user)
        db.commit()
        db.refresh(user)
