import io

from fastapi import UploadFile
from starlette.datastructures import FormData
from sqladmin.application import Admin


async def sqladmin_handle_form_data(self, request, obj=None) -> FormData:
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
            f = getattr(obj, key)
            if isinstance(f, str):
                form_data.append((key, f))
                continue
            form_data.append((key, UploadFile(filename=f.name, file=f.open())))
        else:
            form_data.append((key, value))
    return FormData(form_data)


def apply_monkeypatch():
    Admin._handle_form_data = sqladmin_handle_form_data
