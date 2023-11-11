from typing import List, Optional

from app.models.user import User
from config.database import Session


class UserService:
    """
    A service class for handling user-related operations.

    This class provides methods to interact with the User model using SQLAlchemy.
    It encapsulates the logic for querying, adding, updating, and deleting user records in the database.
    """

    def all(self) -> List[User]:
        """
        Retrieves all user records from the database.

        Returns:
            List[User]: A list of User objects.
        Raises:
            Exception: If any database operation fails.
        """
        try:
            session = Session()
            results = session.query(User).all()
        except Exception as e:
            print(f"Error occurred: {e}")
            raise e
        finally:
            session.close()

        return results

    def find(self, id: int) -> Optional[User]:
        """
        Retrieves a single user record by its ID.

        Args:
            id (int): The ID of the user to retrieve.

        Returns:
            Optional[User]: The User object if found, otherwise None.
        Raises:
            Exception: If any database operation fails.
        """
        try:
            session = Session()
            results = session.query(User).filter_by(id=id).first()
        except Exception as e:
            print(f"Error occurred: {e}")
            raise e
        finally:
            session.close()

        return results

    def save(self, data: dict) -> int:
        """
        Adds a new user record to the database.

        Args:
            data (dict): A dictionary containing the user data.

        Returns:
            int: The ID of the newly created user.
        Raises:
            Exception: If any database operation fails.
        """
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

    def update(self, id: int, data: dict) -> User:
        """
        Updates an existing user record in the database.

        Args:
            id (int): The ID of the user to update.
            data (dict): A dictionary containing the updates to be applied.

        Returns:
            User: The updated User object.
        Raises:
            ValueError: If a user with the given ID does not exist.
            Exception: If any other database operation fails.
        """
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

    def delete(self, id: int) -> int:
        """
        Deletes a user record from the database.

        Args:
            id (int): The ID of the user to delete.

        Returns:
            int: The ID of the deleted user.
        Raises:
            Exception: If any database operation fails.
        """
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
