from typing import Literal
from pydantic import BaseModel, Field, field_validator
from datetime import date
import re


class UserCreateInput(BaseModel):
    user_id: str
    password: str
    nickname: str
    gender: Literal["male", "female"]
    birthday: str = Field(..., description="사용자의 생일. 형식: YYYY-MM-DD")

    @field_validator("birthday")
    @classmethod
    def validate_birthday(cls, v: str) -> str:
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", v):
            raise ValueError("형식은 YYYY-MM-DD이어야 합니다.")

        try:
            year, month, day = map(int, v.split("-"))
            date(year, month, day)

        except ValueError:
            raise ValueError("유효하지 않은 날짜입니다.")

        return v


class LoginInput(BaseModel):
    user_id: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
