from typing import Any

from fastapi import UploadFile
from markupsafe import Markup
from sqladmin import ModelView
from sqlalchemy.orm import object_session
from starlette.requests import Request
from wtforms import (
    Form,
    StringField,
    IntegerField,
    TextAreaField,
    validators,
    FileField,
)

from application.models import User, Diary, StoreItem, UserItem
from application.utils import write_file, remove_file
from config.settings import settings


class FileUploadField(FileField):
    def process_formdata(self, valuelist: list[UploadFile]):
        if valuelist:
            if isinstance(valuelist[0], str):
                self.data = valuelist[0]
                return
            path = write_file("admin", valuelist[0])
            self.data = path


class UserAdmin(ModelView, model=User):
    name = "사용자"
    name_plural = "사용자 관리"
    icon = "fa-solid fa-user"

    can_create = False

    column_labels = {
        User.id: "사용자 ID",
        User.login_id: "로그인 ID",
        User.nickname: "닉네임",
        User.coin: "보유 코인",
        User.items: "보유 아이템들",
        User.created_at: "가입일시",
        User.updated_at: "수정일시",
    }
    column_formatters = {
        User.coin: lambda m, _: f"{m.coin} 코인",
        User.created_at: lambda m, _: m.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        User.updated_at: lambda m, _: m.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
    }

    column_formatters_detail = {
        User.created_at: lambda m, _: m.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        User.updated_at: lambda m, _: m.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
    }

    column_list = [
        User.id,
        User.login_id,
        User.nickname,
        User.coin,
        User.created_at,
        User.updated_at,
    ]
    column_details_list = [
        User.id,
        User.login_id,
        User.nickname,
        User.coin,
        User.items,
        User.created_at,
        User.updated_at,
    ]

    form_columns = [
        User.login_id,
        User.nickname,
        User.diaries,
        User.coin,
        User.items,
    ]

    async def on_model_change(
        self, data: dict, model: User, is_created: bool, request: Request
    ) -> None:
        original_items_pks = {str(item.id) for item in model.items}
        deleted_items_pks = original_items_pks - set(data["items"])

        session = object_session(model)
        for target_pk in deleted_items_pks:
            item = session.get(UserItem, target_pk)
            if item:
                session.delete(item)


class DiaryAdmin(ModelView, model=Diary):
    name = "일기"
    name_plural = "일기 관리"
    icon = "fa-solid fa-book"

    can_create = False

    column_list = [
        Diary.id,
        Diary.user_id,
        Diary.date,
        Diary.title,
        Diary.created_at,
        Diary.updated_at,
    ]
    column_searchable_list = [
        Diary.title,
        Diary.content,
    ]
    column_details_list = [
        Diary.id,
        Diary.user_id,
        Diary.date,
        Diary.weather,
        Diary.title,
        Diary.content,
        Diary.image_urls,
        Diary.analyzed_emotion,
        Diary.created_at,
        Diary.updated_at,
    ]
    column_formatters = {
        Diary.created_at: lambda m, _: m.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        Diary.updated_at: lambda m, _: m.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
    }
    column_formatters_detail = {
        Diary.created_at: lambda m, _: m.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        Diary.updated_at: lambda m, _: m.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
    }


def format_image_url(model, attribute) -> Markup:
    return Markup(
        f'<img src="http://{settings.SERVER_HOST}/{getattr(model, attribute)}" '
        f'style="max-width: 100px; max-height: 100px;" />'
    )


class StoreItemAdmin(ModelView, model=StoreItem):
    name = "상점 아이템"
    name_plural = "상점 아이템 관리"
    icon = "fa-solid fa-store"

    column_labels = {
        StoreItem.id: "아이템 ID",
        StoreItem.name: "이름",
        StoreItem.category: "카테고리",
        StoreItem.price: "가격",
        StoreItem.description: "설명",
        StoreItem.item_image_url: "상품 이미지 URL",
        StoreItem.applied_image_url: "적용 이미지 URL",
    }
    column_list = [
        StoreItem.id,
        StoreItem.name,
        StoreItem.price,
        StoreItem.description,
        StoreItem.item_image_url,
        StoreItem.applied_image_url,
    ]
    column_details_list = [
        StoreItem.id,
        StoreItem.name,
        StoreItem.price,
        StoreItem.description,
        StoreItem.item_image_url,
        StoreItem.applied_image_url,
    ]

    async def on_model_delete(self, model: Any, request: Request) -> None:
        """
        모델 삭제 시 호출되는 메서드로, 상점 아이템이 삭제될 때 관련된 이미지 파일도 삭제합니다.
        """
        if model.item_image_url:
            remove_file(model.item_image_url)

    column_formatters = {
        "item_image_url": format_image_url,
        "applied_image_url": format_image_url,
    }
    column_formatters_detail = {
        "item_image_url": format_image_url,
        "applied_image_url": format_image_url,
    }

    class StoreItemForm(Form):
        name = StringField("이름", [validators.InputRequired()])
        category = StringField("카테고리", [validators.InputRequired()])
        price = IntegerField("가격", [validators.InputRequired()])
        description = TextAreaField("설명", [validators.InputRequired()])
        item_image_url = FileUploadField("상품 이미지 URL")
        applied_image_url = FileUploadField("적용 이미지 URL")

    form = StoreItemForm


class UserItemAdmin(ModelView, model=UserItem):
    name = "사용자 아이템"
    name_plural = "사용자 아이템 관리"
    icon = "fa-solid fa-box"

    can_create = False

    column_labels = {
        UserItem.id: "아이템 ID",
        UserItem.user: "사용자",
        UserItem.item: "아이템",
        UserItem.equipped: "장착 여부",
        UserItem.created_at: "구매일시",
    }
    column_formatters = {
        UserItem.user: lambda m, _: f"{m.user.nickname}({m.user.login_id})",
        UserItem.item: lambda m, _: f"{m.item.name}({m.item.price}코인)",
        UserItem.equipped: lambda m, _: "장착됨" if m.equipped else "장착 안 됨",
        UserItem.created_at: lambda m, _: m.created_at.strftime("%Y-%m-%d %H:%M:%S"),
    }

    column_list = [
        UserItem.user,
        UserItem.item,
        UserItem.equipped,
        UserItem.created_at,
    ]
    column_details_list = [
        UserItem.id,
        UserItem.user,
        UserItem.item,
        UserItem.equipped,
        UserItem.created_at,
    ]
