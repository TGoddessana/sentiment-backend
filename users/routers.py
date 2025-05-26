from typing import Literal

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from config.db import get_db
from .models import User

router = APIRouter()
from pydantic import BaseModel


class UserCreateInput(BaseModel):
    user_id: str
    password: str
    nickname: str
    gender: Literal["male", "female"]
    birthday: str


@router.post("/")
def create_user(request_body: UserCreateInput, db: Session = Depends(get_db)):
    from datetime import date

    user = User(
        user_id=request_body.user_id,
        hashed_password=request_body.password,  # In a real app, hash the password
        nickname=request_body.nickname,
        gender=request_body.gender,
        birthday=date.fromisoformat(request_body.birthday),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {
        "id": user.id,
        "user_id": user.user_id,
        "nickname": user.nickname,
    }


@router.get("/")
def users(db: Session = Depends(get_db)):
    stmt = db.query(User)
    result = stmt.all()
    return result
