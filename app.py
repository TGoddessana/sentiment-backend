from fastapi import FastAPI

from users.routers import router

app = FastAPI()


def get_api_prefix(version: int, path: str) -> str:
    """
    API 버전과 경로를 기반으로 API 접두사를 생성합니다.
    """
    return f"/api/v{version}/{path}"


app.include_router(
    router=router,
    prefix=get_api_prefix(version=1, path="users"),
    tags=["사용자 API"],
)
