from datetime import datetime

from fastapi import UploadFile
from config.settings import settings


def get_filename(file: UploadFile) -> str:
    """
    랜덤한 문자열을 포함한 파일 이름을 생성합니다.
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{timestamp}_{file.filename}"


def get_uploads_dir(login_id, file: UploadFile) -> str:
    today = datetime.now().date()
    path = f"{settings.UPLOAD_DIR}/{login_id}/{today.year}/{today.month}/{today.day}"
    filename = get_filename(file)
    return f"{path}/{filename}"
