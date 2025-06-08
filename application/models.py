from enum import Enum
from datetime import datetime, date
from typing import List

from sqlalchemy import String, Date, DateTime, func, ForeignKey, JSON, Boolean, false
from sqlalchemy.orm import Mapped, mapped_column, relationship

from application.constants import Emotion
from config.db import Base


class IdModel(Base):
    __abstract__ = True

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )


class TimeStampedModel(Base):
    __abstract__ = True

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


class User(IdModel, TimeStampedModel):
    __tablename__ = "users"

    login_id: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(100))
    nickname: Mapped[str] = mapped_column(String(30))
    coin: Mapped[int] = mapped_column(default=0)

    diaries: Mapped[List["Diary"]] = relationship("Diary", back_populates="user")
    items: Mapped[List["UserItem"]] = relationship("UserItem", back_populates="user")

    @property
    def equipped_accessory(self) -> "StoreItem":
        """
        사용자가 장착한 액세서리 아이템을 반환합니다.
        """
        for user_item in self.items:
            if user_item.equipped and user_item.item.category == ItemCategory.ACCESSORY:
                return user_item.item
        return None

    @property
    def equipped_background(self) -> "StoreItem":
        """
        사용자가 장착한 배경 아이템을 반환합니다.
        """
        for user_item in self.items:
            if (
                user_item.equipped
                and user_item.item.category == ItemCategory.BACKGROUND
            ):
                return user_item.item
        return None

    def add_coin(self, amount: int) -> None:
        """사용자에게 코인을 추가합니다."""
        if amount < 0:
            raise ValueError("코인은 음수로 추가할 수 없습니다.")
        self.coin += amount

    def has_item(self, item: "StoreItem") -> bool:
        """
        사용자가 특정 아이템을 보유하고 있는지 확인합니다.
        """
        return item.id in [user_item.item_id for user_item in self.items]

    def is_item_equipped(self, item: "StoreItem") -> bool:
        """
        사용자가 특정 아이템을 장착하고 있는지 확인합니다.
        """
        for user_item in self.items:
            if user_item.item_id == item.id and user_item.equipped:
                return True
        return False

    def purchase_item(self, item: "StoreItem") -> "UserItem":
        """
        아이템을 구매합니다.
        """
        if self.coin < item.price:
            raise ValueError("코인이 부족합니다.")

        # 이미 구매한 아이템인지 확인
        for user_item in self.items:
            if user_item.item_id == item.id:
                raise ValueError("이미 구매한 아이템입니다.")

        # 코인 차감, 아이템 구매 기록 생성
        self.coin -= item.price
        user_item = UserItem(user_id=self.id, item_id=item.id)

        return user_item

    def equip_item(self, item: "StoreItem") -> None:
        """
        아이템을 장착합니다.
        """
        # 이미 장착된 아이템이 있는지 확인
        for user_item in self.items:
            if user_item.equipped and user_item.item.category == item.category:
                raise ValueError(f"{item.category} 아이템은 하나만 장착할 수 있습니다.")

        # 아이템 장착
        for user_item in self.items:
            if user_item.item_id == item.id:
                user_item.equipped = True
                return

        raise ValueError("구매하지 않은 아이템입니다.")

    def unequip_item(self, item: "StoreItem") -> None:
        """
        아이템을 해제합니다.
        """
        for user_item in self.items:
            if user_item.item_id == item.id:
                if user_item.equipped:
                    user_item.equipped = False
                    return
                else:
                    raise ValueError("이미 해제된 아이템입니다.")
        raise ValueError("장착되지 않은 아이템입니다.")

    def __repr__(self):
        return f"User(id={self.id}, login_id={self.login_id})"


class Diary(IdModel, TimeStampedModel):
    __tablename__ = "diaries"

    weather: Mapped[str] = mapped_column(String(20), nullable=False)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[str] = mapped_column(String(5000), nullable=False)
    date: Mapped[date] = mapped_column(
        Date, nullable=False, default=func.current_date()
    )
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
        return f"Diary(id={self.id}, user_id={self.user_id}, date={self.created_at}, title={self.title})"


class ItemCategory(str, Enum):
    ACCESSORY = "accessory"
    BACKGROUND = "background"


class StoreItem(IdModel):
    __tablename__ = "store_items"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[ItemCategory] = mapped_column(String(12))
    price: Mapped[int] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(String(300), nullable=False)
    item_image_url: Mapped[str] = mapped_column(String(200), nullable=False)
    applied_image_url: Mapped[str] = mapped_column(String(200), nullable=False)

    users: Mapped[List["UserItem"]] = relationship("UserItem", back_populates="item")

    def __repr__(self):
        return f"StoreItem(id={self.id}, name={self.name}, category={self.category}, price={self.price})"


class UserItem(IdModel, TimeStampedModel):
    """사용자가 구매한 아이템을 추적하는 모델"""

    __tablename__ = "user_items"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    item_id: Mapped[int] = mapped_column(ForeignKey("store_items.id"), nullable=False)
    equipped: Mapped[bool] = mapped_column(Boolean, server_default=false())

    user: Mapped["User"] = relationship("User", back_populates="items")
    item: Mapped["StoreItem"] = relationship("StoreItem", back_populates="users")

    def __repr__(self):
        return f"UserItem(user_id={self.user_id}, item_id={self.item_id}, equipped={self.equipped})"
