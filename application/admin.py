from sqladmin import ModelView

from application.models import User, Diary


class UserAdmin(ModelView, model=User):
    name = "사용자"
    name_plural = "사용자 관리"
    icon = "fa-solid fa-user"
    column_list = [
        User.id,
        User.login_id,
        User.nickname,
        User.coin,
        User.created_at,
        User.updated_at,
    ]


class DiaryAdmin(ModelView, model=Diary):
    name = "일기"
    name_plural = "일기 관리"
    icon = "fa-solid fa-book"
    column_list = [Diary.id, Diary.user_id, Diary.title, Diary.created_at]
    column_searchable_list = [Diary.title, Diary.content]
    column_filters = [Diary.user_id, Diary.created_at]
    form_columns = [
        Diary.user_id,
        Diary.weather,
        Diary.title,
        Diary.content,
        Diary.image_urls,
        Diary.analyzed_emotion,
    ]
