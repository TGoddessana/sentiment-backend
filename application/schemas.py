from fastapi import UploadFile
from pydantic import BaseModel, RootModel, Field, field_validator
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
    diary_date: date = Field(
        ...,
        description="작성할 일기의 날짜",
    )
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

    @classmethod
    def from_emotion_enum(cls, emotion_enum):
        return cls(
            name=emotion_enum.name,
            korean_name=emotion_enum.korean_name,
            emoji=emotion_enum.emoji,
            message=emotion_enum.message,
        )


class DiaryResponse(BaseModel):
    id: int
    weather: str
    title: str
    content: str
    image_urls: list[str]
    date: date

    created_at: datetime
    updated_at: datetime

    analyzed_emotion: AnalyzedEmotion | None = None

    @classmethod
    def from_diary(
        cls,
        request: Request,
        diary: Diary,
    ) -> "DiaryResponse":
        return cls(
            id=diary.id,
            weather=diary.weather,
            title=diary.title,
            content=diary.content,
            image_urls=[
                f"{request.base_url}{image_url}" for image_url in diary.image_urls
            ],
            date=diary.date,
            created_at=diary.created_at,
            updated_at=diary.updated_at,
            analyzed_emotion=(
                AnalyzedEmotion.from_emotion_enum(diary.get_analyzed_emotion_enum())
                if diary.get_analyzed_emotion_enum()
                else None
            ),
        )

    @property
    class Config:
        from_attributes = True


class DiaryListParams(BaseModel):
    year_and_month: str = Field(
        ...,
        description="조회할 연도와 월을 'YYYY-MM' 형식으로 입력하세요.",
        pattern=r"^\d{4}-(0[1-9]|1[0-2])$",
    )

    @property
    def year(self) -> int:
        return int(self.year_and_month.split("-")[0])

    @property
    def month(self) -> int:
        return int(self.year_and_month.split("-")[1])


class DiaryCalendarResponse(BaseModel):
    id: int
    weather: str
    title: str
    date: date
    analyzed_emotion: AnalyzedEmotion | None = None

    @classmethod
    def from_diary(
        cls,
        request: Request,
        diary: Diary,
    ) -> "DiaryCalendarResponse":
        return cls(
            id=diary.id,
            weather=diary.weather,
            title=diary.title,
            date=diary.created_at.date(),
            analyzed_emotion=(
                AnalyzedEmotion.from_emotion_enum(diary.get_analyzed_emotion_enum())
                if diary.get_analyzed_emotion_enum()
                else None
            ),
        )


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
                f"{request.base_url}{store_item.item_image_url}"
                if store_item.item_image_url
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
