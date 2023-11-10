from app.services.user import UserService


def run():
    user_service = UserService()

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
        {
            "username": "loki",
            "email": "loki@python-spartan.com",
            "password": "loki",
        },
        {
            "username": "lara",
            "email": "lara@python-spartan.com",
            "password": "lara",
        },
    ]

    for user in users:
        user_service.save(user)
