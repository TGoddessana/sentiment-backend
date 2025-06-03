from fastapi import FastAPI
from sqladmin import Admin

from application.admin import UserAdmin, DiaryAdmin, StoreItemAdmin
from application.routers.users import router as users_router
from application.routers.diaries import router as diaries_router
from application.routers.analysis import router as day_analysis_router
from application.routers.stores import router as stores_router
from config.db import engine
from config.settings import settings


def create_app() -> FastAPI:

    app = FastAPI(title=settings.PROJECT_NAME)

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
