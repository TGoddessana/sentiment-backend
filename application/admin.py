import os
from typing import Any

from fastapi import UploadFile
from sqladmin import ModelView
from starlette.datastructures import FormData
from starlette.requests import Request
from wtforms import (
    Form,
    StringField,
    IntegerField,
    TextAreaField,
    validators,
    FileField,
)

from application.models import User, Diary, StoreItem
from application.utils import write_file, remove_file
from config.settings import settings


class FileUploadField(FileField):
    def process_formdata(self, valuelist: list[UploadFile]):
        if valuelist:
            path = write_file("admin", valuelist[0])
            self.data = path


class UserAdmin(ModelView, model=User):
    name = "사용자"
    name_plural = "사용자 관리"
    icon = "fa-solid fa-user"

    can_create = False

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


class DiaryAdmin(ModelView, model=Diary):
    name = "일기"
    name_plural = "일기 관리"
    icon = "fa-solid fa-book"

    can_create = False
    can_edit = False

    column_list = [
        Diary.id,
        Diary.user_id,
        Diary.title,
        Diary.created_at,
    ]
    column_searchable_list = [
        Diary.title,
        Diary.content,
    ]
    column_details_list = [
        Diary.id,
        Diary.user_id,
        Diary.weather,
        Diary.title,
        Diary.content,
        Diary.image_urls,
        Diary.analyzed_emotion,
        Diary.created_at,
        Diary.updated_at,
    ]


class StoreItemAdmin(ModelView, model=StoreItem):
    name = "상점 아이템"
    name_plural = "상점 아이템 관리"
    icon = "fa-solid fa-store"

    column_list = [
        StoreItem.id,
        StoreItem.name,
        StoreItem.price,
        StoreItem.description,
        StoreItem.image_url,
    ]
    column_details_list = [
        StoreItem.id,
        StoreItem.name,
        StoreItem.price,
        StoreItem.description,
        StoreItem.image_url,
    ]

    async def on_model_delete(self, model: Any, request: Request) -> None:
        """
        모델 삭제 시 호출되는 메서드로, 상점 아이템이 삭제될 때 관련된 이미지 파일도 삭제합니다.
        """
        if model.image_url:
            remove_file(model.image_url)

    class StoreItemForm(Form):
        name = StringField("이름", [validators.InputRequired()])
        category = StringField("카테고리", [validators.InputRequired()])
        price = IntegerField("가격", [validators.InputRequired()])
        description = TextAreaField("설명", [validators.InputRequired()])
        image_url = FileUploadField("이미지 URL", [validators.InputRequired()])

    form = StoreItemForm
