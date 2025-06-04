from typing import Literal

from fastapi import UploadFile
from pydantic import BaseModel, Field, field_validator
from datetime import date, datetime

from starlette.requests import Request

from application.models import Diary, User, StoreItem


class UserResponse(BaseModel):
    id: int
    login_id: str
    nickname: str
    coin: int

    @property
    class Config:
        from_attributes = True


class UserCreateInput(BaseModel):
    login_id: str
    password: str
    nickname: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str


class DiaryCreateInput(BaseModel):
    weather: str = Field(..., description="날씨")
    title: str = Field(..., description="제목")
    content: str = Field(..., description="일기 본문")
    image_files: list[UploadFile] = Field(default=[], description="이미지 파일들")

    @field_validator("image_files")
    @classmethod
    def validate_image_files(cls, files):
        max_files = 5
        max_size = 5 * 1024 * 1024
        if len(files) > max_files:
            raise ValueError(f"이미지는 최대 {max_files}장까지 업로드할 수 있습니다.")
        for file in files:
            if hasattr(file, "size"):
                size = file.size
            elif (
                hasattr(file, "file")
                and hasattr(file.file, "seek")
                and hasattr(file.file, "tell")
            ):
                pos = file.file.tell()
                file.file.seek(0, 2)
                size = file.file.tell()
                file.file.seek(pos)
            else:
                size = None
            if size is not None and size > max_size:
                raise ValueError(f"이미지 한 장의 크기는 5MB를 넘을 수 없습니다.")
        return files


class AnalyzedEmotion(BaseModel):
    name: str
    korean_name: str
    emoji: str
    message: str


class DiaryResponse(BaseModel):
    id: int
    weather: str
    title: str
    content: str
    image_urls: list[str]
    date: date
    analyzed_emotion: AnalyzedEmotion | None = None

    @classmethod
    def from_diary(cls, diary: Diary) -> "DiaryResponse":
        return cls(
            id=diary.id,
            weather=diary.weather,
            title=diary.title,
            content=diary.content,
            image_urls=diary.image_urls,
            date=diary.created_at.date(),
            analyzed_emotion=(
                AnalyzedEmotion(
                    name=(
                        diary.get_analyzed_emotion_enum().name
                        if diary.get_analyzed_emotion_enum()
                        else None
                    ),
                    korean_name=(
                        diary.get_analyzed_emotion_enum().korean_name
                        if diary.get_analyzed_emotion_enum()
                        else None
                    ),
                    emoji=(
                        diary.get_analyzed_emotion_enum().emoji
                        if diary.get_analyzed_emotion_enum()
                        else None
                    ),
                    message=(
                        diary.get_analyzed_emotion_enum().message
                        if diary.get_analyzed_emotion_enum()
                        else None
                    ),
                )
                if diary.get_analyzed_emotion_enum()
                else None
            ),
        )

    @property
    class Config:
        from_attributes = True


class WeeklySummary(BaseModel):
    week_number: int
    summary: str


class MonthlyAnalysis(BaseModel):
    weekly_emotions: list
    weekly_summaries: list[WeeklySummary]  # 4주치 주간 조언


#########
# STORE #
#########


class StoreItemResponse(BaseModel):
    id: int
    name: str
    category: str
    description: str
    price: int
    image_url: str | None

    purchased: bool
    equipped: bool

    @classmethod
    def from_store_item(
        cls,
        request: Request,
        store_item: StoreItem,
        current_user: User,
    ) -> "StoreItemResponse":
        return cls(
            id=store_item.id,
            name=store_item.name,
            category=store_item.category,
            description=store_item.description,
            price=store_item.price,
            image_url=(
                f"{request.base_url}{store_item.image_url}"
                if store_item.image_url
                else None
            ),
            purchased=current_user.has_item(item=store_item),
            equipped=current_user.is_item_equipped(item=store_item),
        )

    @property
    class Config:
        from_attributes = True


class UserItemResponse(BaseModel):
    id: int
    item: StoreItemResponse
    purchased_at: datetime

    @property
    class Config:
        from_attributes = True
