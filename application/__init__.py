from fastapi import FastAPI
from sqladmin import Admin
from starlette.staticfiles import StaticFiles

from application.admin import UserAdmin, DiaryAdmin
from application.routers.users import router as users_router
from application.routers.diaries import router as diaries_router
from application.routers.analysis import router as day_analysis_router
from config.db import engine
from config.settings import settings


def create_app() -> FastAPI:

    app = FastAPI(title=settings.PROJECT_NAME)

    # Admin setup
    admin = Admin(app, engine=engine, title=settings.ADMIN_TITLE)
    admin.add_view(UserAdmin)
    admin.add_view(DiaryAdmin)

    # Static files for uploads
    app.mount(
        f"/{settings.UPLOAD_DIR}",
        StaticFiles(directory=settings.UPLOAD_DIR),
        name="uploads",
    )

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

    return app
