from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from config.dependencies import SessionDependency, CurrentUser
from config.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
)
from application.models import User
from application.schemas import (
    UserCreateInput,
    TokenResponse,
    UserResponse,
)

router = APIRouter()


@router.post(
    "/signup",
    status_code=status.HTTP_201_CREATED,
    summary="회원가입",
    description="사용자 정보를 입력받아 새로운 사용자를 생성하는 API입니다.",
)
def create_user(
    request_body: UserCreateInput,
    db_session: SessionDependency,
):
    if db_session.query(User).filter(User.login_id == request_body.login_id).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 존재하는 사용자 ID입니다.",
        )

    user = User(
        login_id=request_body.login_id,
        hashed_password=get_password_hash(request_body.password),
        nickname=request_body.nickname,
    )
    db_session.add(user)
    db_session.flush()
    db_session.refresh(user)

    return {
        "id": user.id,
        "login_id": user.login_id,
        "nickname": user.nickname,
    }


@router.get(
    "/me",
    response_model=UserResponse,
    summary="현재 사용자 정보",
    description="현재 로그인된 사용자의 정보를 반환하는 API입니다.",
)
def read_current_user(current_user: CurrentUser):
    return current_user


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="로그인",
    description="사용자 ID와 비밀번호를 입력받아 로그인하고, 액세스 토큰과 리프레시 토큰을 반환하는 API입니다.",
)
def login(
    db_session: SessionDependency,
    oauth2_formdata: OAuth2PasswordRequestForm = Depends(),
):
    user = (
        db_session.query(User).filter(User.login_id == oauth2_formdata.username).first()
    )

    if not user or not verify_password(oauth2_formdata.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="잘못된 사용자 ID 또는 비밀번호입니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(str(user.login_id))
    refresh_token = create_refresh_token(str(user.login_id))

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )
