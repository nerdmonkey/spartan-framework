from app.services.user import UserService

def run():
    user_service = UserService()

    users = [
        {"username": "andeng", "email": "andeng@python-spartan.com", "password": "andeng"},
        {"username": "iviang", "email": "iviang@python-spartan.com", "password": "iviang"},
        {"username": "loki", "email": "loki@python-spartan.com", "password": "loki"},
        {"username": "lara", "email": "lara@python-spartan.com", "password": "lara"},
        {"username": "zeus", "email": "zeus@python-spartan.com", "password": "zeus123"},
        {"username": "hera", "email": "hera@python-spartan.com", "password": "hera123"},
        {"username": "athena", "email": "athena@python-spartan.com", "password": "athena123"},
        {"username": "apollo", "email": "apollo@python-spartan.com", "password": "apollo123"},
        {"username": "artemis", "email": "artemis@python-spartan.com", "password": "artemis123"},
        {"username": "hades", "email": "hades@python-spartan.com", "password": "hades123"},
    ]

    for user in users:
        user_service.save(user)
