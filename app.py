from fastapi import FastAPI

from application.routers.users import router as users_router
from application.routers.diaries import router as diaries_router
from application.routers.analysis import router as day_analysis_router
from config.settings import settings

app = FastAPI(title=settings.PROJECT_NAME)


def get_api_prefix(version: int, path: str) -> str:
    """
    API 버전과 경로를 기반으로 API 접두사를 생성합니다.
    """
    return f"/api/v{version}/{path}"


app.include_router(
    router=users_router,
    prefix=get_api_prefix(version=1, path="users"),
    tags=["사용자 API"],
)
app.include_router(
    router=diaries_router,
    prefix=get_api_prefix(version=1, path="diaries"),
    tags=["일기 API"],
)
app.include_router(
    router=day_analysis_router,
    prefix=get_api_prefix(version=1, path="analysis"),
    tags=["감정분석 API"],
)
