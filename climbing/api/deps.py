from os import makedirs, path
from shutil import copyfileobj
from uuid import uuid4

from fastapi import Header, HTTPException, UploadFile, status

from climbing.core.config import settings


class FileStorage:
    def __init__(self) -> None:
        if not path.exists(settings.MEDIA_ROOT):
            makedirs(settings.MEDIA_ROOT)

    def save(self, file: UploadFile) -> str:
        filename = uuid4().hex + path.splitext(file.filename)[1]
        full_filename = path.join(settings.MEDIA_ROOT, filename)
        with open(full_filename, "wb") as out_file:
            copyfileobj(file.file, out_file)
        return full_filename


def multipart_form_data(content_type: str = Header(...)):
    """Force request MIME-type to multipart/form-data"""

    if content_type != "multipart/form-data":
        raise HTTPException(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Unsupported media type: {content_type}."
            " It must be multipart/form-data",
        )
