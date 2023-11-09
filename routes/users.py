from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.models.user import User
from config.database import Session
from app.requests.user import UserCreateRequest, UserEditRequest

def get_db():
    try:
        db = Session()
        yield db
    finally:
        db.close()

route = APIRouter(
    prefix="/api",
    tags=["Users"],
    responses={404: {"description": "Not found"}}
)

@route.get("/users", status_code=200)
async def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@route.get("/users/{user_id}", status_code=200)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@route.post("/users", status_code=201)
async def create_user(user: UserCreateRequest, db: Session = Depends(get_db)):
    hashed_password = user.password
    db_user = User(username=user.username, email=user.email, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@route.put("/users/{user_id}", status_code=200)
async def update_user(user_id: int, user: UserEditRequest, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user_data = user.dict(exclude_unset=True)
    if 'password' in user_data:
        user_data['password'] = user_data['password']
    for key, value in user_data.items():
        setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user

@route.delete("/users/{user_id}", status_code=204)
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return {"ok": True}
