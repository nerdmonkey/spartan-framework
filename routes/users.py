from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.requests.user import UserCreateRequest, UserUpdateRequest
from app.responses.user import UserCreateResponse, UserResponse, UserUpdateResponse
from app.services.user import UserService
from config.database import get_session

user_service = UserService(db=None)

route = APIRouter(
    prefix="/api", tags=["Users"], responses={404: {"description": "Not found"}}
)


@route.get("/users", status_code=200, response_model=List[UserResponse])
async def get_users(
    page: Optional[int] = Query(1, description="Page number", gt=0),
    items_per_page: Optional[int] = Query(10, description="Items per page", gt=0),
    db: Session = Depends(get_session),
):
    """
    Get a list of users with pagination.

    Args:
        page (int): The page number.
        items_per_page (int): Number of items per page.
        db (Session): SQLAlchemy database session.

    Returns:
        List[UserResponse]: List of user objects.
    """
    try:
        user_service.db = db
        return user_service.all(page, items_per_page)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@route.get("/users/{id}", status_code=200, response_model=UserResponse)
async def get_user(id: int, db: Session = Depends(get_session)):
    """
    Get a user by their unique identifier.

    Args:
        id (int): The unique identifier of the user.
        db (Session): SQLAlchemy database session.

    Returns:
        UserResponse: User object.
    """
    try:
        user_service.db = db
        user = user_service.find(id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@route.post("/users", status_code=201, response_model=UserCreateResponse)
async def create_user(user: UserCreateRequest, db: Session = Depends(get_session)):
    """
    Create a new user.

    Args:
        user (UserCreateRequest): User creation request.
        db (Session): SQLAlchemy database session.

    Returns:
        UserCreateResponse: Created user object.
    """
    try:
        user_service.db = db
        created_user = user_service.save(user)
        return created_user
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@route.put("/users/{id}", status_code=200, response_model=UserUpdateResponse)
async def update_user(
    id: int, user: UserUpdateRequest, db: Session = Depends(get_session)
):
    """
    Update an existing user's information.

    Args:
        id (int): The unique identifier of the user to update.
        user (UserUpdateRequest): User update request.
        db (Session): SQLAlchemy database session.

    Returns:
        UserUpdateResponse: Updated user object.
    """
    try:
        user_service.db = db
        updated_user = user_service.update(id, user)
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")
        return updated_user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@route.delete("/users/{id}", status_code=204)
async def delete_user(id: int, db: Session = Depends(get_session)):
    """
    Delete a user by their unique identifier.

    Args:
        id (int): The unique identifier of the user to delete.
        db (Session): SQLAlchemy database session.
    """
    try:
        user_service.db = db
        success = user_service.delete(id)
        if not success:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
