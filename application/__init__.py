import io

from fastapi import FastAPI, UploadFile
from sqladmin import Admin
from starlette.datastructures import FormData
from fastapi.middleware.cors import CORSMiddleware

from application.admin import UserAdmin, DiaryAdmin, StoreItemAdmin
from application.routers.users import router as users_router
from application.routers.diaries import router as diaries_router
from application.routers.analysis import router as day_analysis_router
from application.routers.stores import router as stores_router
from config.db import engine
from config.settings import settings

import sqladmin.application


async def _handle_form_data(self, request, obj=None) -> FormData:
    form = await request.form()
    form_data: list[tuple[str, str | UploadFile]] = []
    for key, value in form.multi_items():
        if not isinstance(value, UploadFile):
            form_data.append((key, value))
            continue

        should_clear = form.get(key + "_checkbox")
        empty_upload = len(await value.read(1)) != 1
        await value.seek(0)
        if should_clear:
            form_data.append((key, UploadFile(io.BytesIO(b""))))
        elif empty_upload and obj and getattr(obj, key):
            f = getattr(obj, key)  # In case of update, imitate UploadFile
            if isinstance(f, str):
                form_data.append((key, f))
                continue
            form_data.append((key, UploadFile(filename=f.name, file=f.open())))
        else:
            form_data.append((key, value))
    return FormData(form_data)


sqladmin.application.Admin._handle_form_data = _handle_form_data


def create_app() -> FastAPI:

    app = FastAPI(title=settings.PROJECT_NAME)

    # Middleware setup
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.TRUSTED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Admin setup
    admin = Admin(app, engine=engine, title=settings.ADMIN_TITLE)
    admin.add_view(UserAdmin)
    admin.add_view(DiaryAdmin)
    admin.add_view(StoreItemAdmin)

    # Include routers
    app.include_router(
        router=users_router,
        prefix="/api/v1/users",
        tags=["사용자 API"],
    )
    app.include_router(
        router=diaries_router,
        prefix="/api/v1/diaries",
        tags=["일기 API"],
    )
    app.include_router(
        router=day_analysis_router,
        prefix="/api/v1/analysis",
        tags=["감정분석 API"],
    )
    app.include_router(
        router=stores_router,
        prefix="/api/v1/stores",
        tags=["상점 API"],
    )

    return app
