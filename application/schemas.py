from typing import Literal, List, Optional
from pydantic import BaseModel, Field, field_validator
from datetime import date, datetime
import re


class UserCreateInput(BaseModel):
    login_id: str
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
    login_id: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str


class DiaryCreateInput(BaseModel):
    date: str = Field(..., description="일기 날짜. 형식: YYYY-MM-DD")
    weather: str = Field(..., description="날씨")
    title: str = Field(..., description="제목")
    content: str = Field(..., description="일기 본문")
    image_urls: Optional[List[str]] = Field(
        default=[], description="첨부 이미지 URL들 (최대 5장)"
    )

    @field_validator("date")
    @classmethod
    def validate_date(cls, v: str) -> str:
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", v):
            raise ValueError("형식은 YYYY-MM-DD이어야 합니다.")

        try:
            year, month, day = map(int, v.split("-"))
            date(year, month, day)
        except ValueError:
            raise ValueError("유효하지 않은 날짜입니다.")

        return v

    @field_validator("image_urls")
    @classmethod
    def validate_image_urls(cls, v: List[str]) -> List[str]:
        if len(v) > 5:
            raise ValueError("이미지는 최대 5개까지만 첨부할 수 있습니다.")
        return v


class DiaryResponse(BaseModel):
    id: int
    user_id: int
    date: date
    weather: str
    title: str
    content: str
    image_urls: List[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
