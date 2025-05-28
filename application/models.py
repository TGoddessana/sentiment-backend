from datetime import datetime, date
from typing import Literal, List

from sqlalchemy import String, Date, DateTime, func, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
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
    gender: Mapped[Literal["male", "female"]] = mapped_column(String(6))
    birthday: Mapped[date] = mapped_column()
    coin: Mapped[int] = mapped_column(default=0)

    diaries: Mapped[List["Diary"]] = relationship("Diary", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, login_id={self.login_id})>"


class Diary(Base, IdMixin, TimeStampedMixin):
    __tablename__ = "diaries"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    weather: Mapped[str] = mapped_column(String(20), nullable=False)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[str] = mapped_column(String(5000), nullable=False)
    image_urls: Mapped[List[str]] = mapped_column(JSON, default=list)

    user: Mapped["User"] = relationship("User", back_populates="diaries")

    def __repr__(self):
        return f"<Diary(id={self.id}, user_id={self.user_id}, date={self.date}, title={self.title})>"
