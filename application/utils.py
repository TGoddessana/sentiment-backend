import os
from datetime import datetime

from fastapi import UploadFile
from config.settings import settings


def write_file(child_folder_name: str, file: UploadFile) -> str:
    """
    주어진 파일을 지정된 폴더에 저장하고, 저장된 파일의 경로를 반환합니다.

    :param: child_folder_name: 파일을 저장할 하위 폴더 이름
    :return: 저장된 파일의 경로
    """
    try:
        upload_path = get_upload_path(child_folder_name, file)
        os.makedirs(os.path.dirname(upload_path), exist_ok=True)
        with open(upload_path, "wb") as f:
            f.write(file.file.read())
        return upload_path
    except Exception as e:
        raise RuntimeError(f"파일 업로드 중 오류 발생: {e}")
    finally:
        file.file.close()


def remove_file(file_path: str) -> None:
    """
    주어진 파일 경로의 파일을 삭제합니다.
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        raise RuntimeError(f"파일 삭제 중 오류 발생: {e}")


def get_timestamped_filename(file_name: str) -> str:
    """
    랜덤한 문자열을 포함한 파일 이름을 생성합니다.
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{timestamp}_{file_name}"


def get_upload_path(login_id, file: UploadFile) -> str:
    """
    주어진 사용자 ID와 파일로부터 업로드 경로를 생성합니다.
    """
    today = datetime.now().date()
    path = f"{settings.UPLOAD_DIR}/{login_id}/{today.year}/{today.month}/{today.day}"
    timestamped_filename = get_timestamped_filename(file.filename)
    return f"{path}/{timestamped_filename}"
