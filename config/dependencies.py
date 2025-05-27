from typing import Annotated

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt import InvalidTokenError
from pydantic import ValidationError, BaseModel
from sqlalchemy.orm import Session
from starlette import status

from config.db import SessionLocal
from config.settings import settings
from users.models import User


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


SessionDependency = Annotated[Session, Depends(get_db)]
Token = Annotated[str, Depends(OAuth2PasswordBearer(tokenUrl=f"api/v1/users/login"))]


def get_current_user(session: SessionDependency, token: Token) -> User:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        token_data = payload.get("sub")
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="유효하지 않은 토큰입니다.",
        )

    user = session.query(User).filter(User.user_id == token_data).first()

    if not user:
        raise HTTPException(status_code=404, detail="없는 사용자입니다.")

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
