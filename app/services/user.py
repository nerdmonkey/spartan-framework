from app.models.user import User
from config.database import Session


class UserService:
    def all(self):
        try:
            session = Session()
            results = session.query(User).all()
        except Exception as e:
            print(f"Error occured: {e}")
            raise e
        finally:
            session.close()

        return results

    def find(self, id: int):
        try:
            session = Session()
            results = session.query(User).filter_by(id=id).first()
        except Exception as e:
            print(f"Error occured: {e}")
            raise e
        finally:
            session.close()

        return results

    def save(self, data: dict = None):
        try:
            session = Session()
            new_data = User(**data)
            session.add(new_data)
            session.commit()
            session.refresh(new_data)

        except Exception as e:
            session.rollback()
            raise e

        finally:
            session.close()

        return new_data.id

    def update(self, id: int = None, data: dict = None):
        try:
            session = Session()
            user = session.query(User).filter_by(id=id).first()

            if user:
                for key, value in data.items():
                    setattr(user, key, value)

                session.commit()

            else:
                raise ValueError(f"User with ID {id} not found")

        except Exception as e:
            session.rollback()

            raise e

        finally:
            session.close()

        return user

    def update(self, id: int = None, data: dict = None):
        try:
            with Session() as session:
                user = session.query(User).filter_by(id=id).first()

                if user:
                    for key, value in data.items():
                        setattr(user, key, value)

                    session.commit()

                else:
                    raise ValueError(f"User with ID {id} not found")

        except Exception as e:
            session.rollback()

            raise e

        return user

    def delete(self, id: int):
        try:
            session = Session()
            session.query(User).filter_by(id=id).delete()
            session.commit()

        except Exception as e:
            session.rollback()
            raise e

        finally:
            session.close()

        return id
