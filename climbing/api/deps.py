from os import makedirs, path, remove
from shutil import copyfileobj
from urllib.parse import urljoin
from uuid import uuid4

from fastapi import Header, HTTPException, UploadFile, status

from climbing.core.config import settings


class FileStorage:  # pylint: disable=too-few-public-methods
    """Class for managing file storage

    Attributes:
        root (str): path to root folder of file storage
    """

    root: str

    def __init__(self, root: str = settings.MEDIA_ROOT) -> None:
        self.root = root
        if not path.exists(root):
            makedirs(root)

    def save(self, file: UploadFile) -> str:
        """Saves file and returns path to it (join(root, generated_filename))

        Params:
            file (UploadFile): file
        """
        filename = uuid4().hex + path.splitext(file.filename)[1]
        # Use unix separators
        full_filename = urljoin(self.root + "/", filename)
        with open(full_filename, "wb") as out_file:
            copyfileobj(file.file, out_file)
        return full_filename

    def remove(self, filename: str) -> None:
        remove(filename)

    def remove_relative(self, filename: str) -> None:
        remove(path.join(self.root, filename))

    def exists(self, filename: str) -> bool:
        return path.exists(filename)

    def exists_relative(self, filename) -> bool:
        return path.exists(path.join(self.root, filename))


def multipart_form_data(content_type: str = Header(...)):
    """Force request MIME-type to multipart/form-data"""

    if content_type != "multipart/form-data":
        raise HTTPException(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Unsupported media type: {content_type}."
            " It must be multipart/form-data",
        )
