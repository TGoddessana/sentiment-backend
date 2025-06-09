import calendar

from fastapi import UploadFile
from pydantic import BaseModel, Field, field_validator
from datetime import date, datetime

from pydantic_core.core_schema import ValidationInfo
from starlette.requests import Request

from application.constants import MindContentType
from application.models import Diary, User, StoreItem


class UserResponse(BaseModel):
    id: int
    login_id: str
    nickname: str
    coin: int

    equipped_accessory_image_url: str | None = None
    equipped_background_image_url: str | None = None

    @classmethod
    def from_user(
        cls,
        request: Request,
        user: User,
    ) -> "UserResponse":

        return cls(
            id=user.id,
            login_id=user.login_id,
            nickname=user.nickname,
            coin=user.coin,
            equipped_accessory_image_url=(
                f"{request.base_url}{user.equipped_accessory.applied_image_url}"
                if user.equipped_accessory and user.equipped_accessory.applied_image_url
                else None
            ),
            equipped_background_image_url=(
                f"{request.base_url}{user.equipped_background.applied_image_url}"
                if user.equipped_background
                and user.equipped_background.applied_image_url
                else None
            ),
        )

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
            image_urls=(
                [f"{request.base_url}{image_url}" for image_url in diary.image_urls]
                if diary.image_urls
                else []
            ),
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


class MindContentRecommendationResponse(BaseModel):
    level: int
    name: str
    korean_name: str
    instruction: list[str]

    @classmethod
    def from_mind_content_type(cls, mind_content_type: MindContentType):
        return cls(
            level=mind_content_type.level,
            name=mind_content_type.name,
            korean_name=mind_content_type.korean_name,
            instruction=mind_content_type.instruction,
        )


class MindContentCreateRequest(BaseModel):
    class _SelfPraiseContent(BaseModel):
        sentence1: str = Field(..., description="자기 칭찬 문장 1")
        sentence2: str = Field(..., description="자기 칭찬 문장 2")
        sentence3: str = Field(..., description="자기 칭찬 문장 3")

    level: int
    self_praise_content: _SelfPraiseContent

    @field_validator("level")
    @classmethod
    def validate_level(cls, value, info: ValidationInfo):
        if value not in [1, 2, 3]:
            raise ValueError("유효한 마음챙김 콘텐츠 레벨은 1, 2, 3입니다.")
        return value


class WeeklyReportRequest(BaseModel):
    start_date: date = Field(
        ...,
        description="주간 리포트의 시작 날짜 (월요일)",
    )
    end_date: date = Field(
        ...,
        description="주간 리포트의 끝 날짜 (일요일)",
    )

    @field_validator("start_date")
    @classmethod
    def validate_dates(cls, value, info: ValidationInfo):
        if value.weekday() != 0:
            raise ValueError("시작 날짜는 월요일이어야 합니다.")
        return value

    @field_validator("end_date")
    @classmethod
    def validate_end_date(cls, value, info: ValidationInfo):
        if value.weekday() != 6:
            raise ValueError("끝 날짜는 일요일이어야 합니다.")
        return value


class MonthlyReportRequest(BaseModel):
    start_date: date = Field(
        ...,
        description="월간 리포트의 시작 날짜 (1일)",
    )
    end_date: date = Field(
        ...,
        description="월간 리포트의 끝 날짜 (마지막 날)",
    )

    @field_validator("start_date")
    @classmethod
    def validate_start_date(cls, value, info: ValidationInfo):
        if value.day != 1:
            raise ValueError("시작 날짜는 1일이어야 합니다.")
        return value

    @field_validator("end_date")
    @classmethod
    def validate_end_date(cls, value, info: ValidationInfo):
        last_day_of_month = calendar.monthrange(value.year, value.month)[1]
        if value.day != last_day_of_month:
            raise ValueError(f"끝 날짜는 {last_day_of_month}일이어야 합니다.")
        return value


#########
# STORE #
#########


class StoreItemResponse(BaseModel):
    id: int
    name: str
    category: str
    description: str
    price: int

    item_image_url: str | None
    applied_image_url: str | None

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
            item_image_url=(
                f"{request.base_url}{store_item.item_image_url}"
                if store_item.item_image_url
                else None
            ),
            applied_image_url=(
                f"{request.base_url}{store_item.applied_image_url}"
                if store_item.applied_image_url
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
