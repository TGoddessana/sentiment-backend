from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from sqladmin import Admin
from fastapi.middleware.cors import CORSMiddleware
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse

from application.admin import (
    UserAdmin,
    DiaryAdmin,
    StoreItemAdmin,
    UserItemAdmin,
    WeeklyReportAdmin,
    MonthlyReportAdmin,
    MindContentAdmin,
)
from application.monkeypatch import apply_monkeypatch
from application.routers.users import router as users_router
from application.routers.diaries import router as diaries_router
from application.routers.analysis import router as day_analysis_router
from application.routers.stores import router as stores_router
from config.db import engine
from config.settings import settings


def create_app() -> FastAPI:
    apply_monkeypatch()

    app = FastAPI(title=settings.PROJECT_NAME)

    @app.exception_handler(Exception)
    async def internal_server_error(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "서버 내부 오류가 발생했습니다."},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        err = exc.errors()[0]
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": str(err["msg"])},
        )

    # Middleware setup
    app.add_middleware(
        CORSMiddleware,  # type: ignore
        allow_origins=settings.TRUSTED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Admin setup
    admin = Admin(app, engine=engine, title=settings.ADMIN_TITLE)
    admin.add_view(UserAdmin)
    admin.add_view(DiaryAdmin)
    admin.add_view(MindContentAdmin)
    admin.add_view(WeeklyReportAdmin)
    admin.add_view(MonthlyReportAdmin)
    admin.add_view(StoreItemAdmin)
    admin.add_view(UserItemAdmin)

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
