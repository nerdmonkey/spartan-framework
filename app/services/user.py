from typing import List, Optional
from contextlib import contextmanager
from sqlalchemy.exc import SQLAlchemyError
from app.models.user import User
from config.database import Session

class UserService:
    """
    A service class for handling user-related operations.
    Provides methods to interact with the User model using SQLAlchemy.
    """

    @contextmanager
    def session_scope(self):
        """Provide a transactional scope around a series of operations."""
        session = Session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def all(self) -> List[User]:
        """Retrieves all user records from the database."""
        with self.session_scope() as session:
            return session.query(User).all()

    def find(self, id: int) -> Optional[User]:
        """Retrieves a single user record by its ID."""
        with self.session_scope() as session:
            return session.query(User).filter_by(id=id).first()

    def save(self, data: dict) -> int:
        """Adds a new user record to the database."""
        with self.session_scope() as session:
            new_user = User(**data)
            session.add(new_user)
            session.flush()
            return new_user.id

    def update(self, id: int, data: dict) -> User:
        """Updates an existing user record in the database."""
        with self.session_scope() as session:
            user = session.query(User).filter_by(id=id).first()
            if not user:
                raise ValueError(f"User with ID {id} not found")

            for key, value in data.items():
                setattr(user, key, value)
            return user

    def delete(self, id: int) -> int:
        """Deletes a user record from the database."""
        with self.session_scope() as session:
            session.query(User).filter_by(id=id).delete()
            return id
