from datetime import datetime, date
from typing import Literal, List

from sqlalchemy import String, Date, DateTime, func, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from application.constants import Emotion
from config.db import Base


class IdMixin:
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)


class TimeStampedMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class User(Base, IdMixin, TimeStampedMixin):
    __tablename__ = "users"

    login_id: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(100))
    nickname: Mapped[str] = mapped_column(String(30))
    coin: Mapped[int] = mapped_column(default=0)

    diaries: Mapped[List["Diary"]] = relationship("Diary", back_populates="user")

    def add_coin(self, amount: int) -> None:
        """사용자에게 코인을 추가합니다."""
        if amount < 0:
            raise ValueError("코인은 음수로 추가할 수 없습니다.")
        self.coin += amount

    def __repr__(self):
        return f"<User(id={self.id}, login_id={self.login_id})>"


class Diary(Base, IdMixin, TimeStampedMixin):
    __tablename__ = "diaries"

    weather: Mapped[str] = mapped_column(String(20), nullable=False)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[str] = mapped_column(String(5000), nullable=False)
    image_urls: Mapped[List[str]] = mapped_column(JSON, default=list)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    analyzed_emotion: Mapped[str] = mapped_column(String(10), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="diaries")

    def analyze_emotion(self, emotion: Emotion) -> None:
        """일기에 감정 분석 결과를 추가합니다."""
        self.analyzed_emotion = emotion.name

    def get_analyzed_emotion_enum(self) -> Emotion | None:
        return (
            Emotion.from_name(self.analyzed_emotion) if self.analyzed_emotion else None
        )

    def __repr__(self):
        return f"<Diary(id={self.id}, user_id={self.user_id}, date={self.date}, title={self.title})>"


class StoreItem(Base, IdMixin):
    __tablename__ = "store_items"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[Literal["accessory", "background"]] = mapped_column(String(6))
    price: Mapped[int] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(String(300), nullable=False)
    image_url: Mapped[str] = mapped_column(String(200), nullable=False)

    def __repr__(self):
        return f"<StoreItem(id={self.id}, name={self.name}, category={self.category}, price={self.price})>"
