import logging
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from config.dependencies import get_db, SessionDependency, CurrentUser
from config.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
)
from .models import User
from .schemas import UserCreateInput, LoginInput, TokenResponse

router = APIRouter()


@router.post(
    "/signup",
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    request_body: UserCreateInput,
    db_session: SessionDependency,
):
    if db_session.query(User).filter(User.user_id == request_body.user_id).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 존재하는 사용자 ID입니다.",
        )

    user = User(
        user_id=request_body.user_id,
        hashed_password=get_password_hash(request_body.password),
        nickname=request_body.nickname,
        gender=request_body.gender,
        birthday=date.fromisoformat(request_body.birthday),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return {
        "id": user.id,
        "user_id": user.user_id,
        "nickname": user.nickname,
    }


@router.get("/")
def read_user_list(db: Session = Depends(get_db)):
    stmt = db.query(User)
    result = stmt.all()
    return result


@router.get("/me")
def read_current_user(current_user: CurrentUser):
    return {
        "id": current_user.id,
        "user_id": current_user.user_id,
        "nickname": current_user.nickname,
    }


@router.get("/{user_id}")
def read_user(user_id: str, db: Session = Depends(get_db)):
    stmt = db.query(User).filter(User.user_id == user_id)
    result = stmt.first()

    if not result:
        return {"error": "User not found"}

    return {
        "id": result.id,
        "user_id": result.user_id,
        "nickname": result.nickname,
    }


@router.delete("/{user_id}")
def delete_user(user_id: str, db: Session = Depends(get_db)):
    stmt = db.query(User).filter(User.user_id == user_id)
    result = stmt.first()

    if not result:
        return {"error": "User not found"}

    db.delete(result)
    db.commit()

    return {"message": "User deleted successfully"}


@router.post("/login", response_model=TokenResponse)
def login(
    oauth2_formdata: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.user_id == oauth2_formdata.username).first()

    if not user or not verify_password(oauth2_formdata.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(str(user.user_id))
    refresh_token = create_refresh_token(str(user.user_id))

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )
