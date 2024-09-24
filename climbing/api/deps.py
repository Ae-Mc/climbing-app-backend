from mimetypes import guess_extension
from uuid import uuid4

from fastapi import Header, HTTPException, UploadFile, status
from minio import Minio, S3Error

from climbing.core import responses
from climbing.core.config import settings


class FileStorage:  # pylint: disable=too-few-public-methods
    """Class for managing file storage

    Attributes:
        root (str): path to root folder of file storage
    """

    client: Minio

    def __init__(self) -> None:
        self.client = Minio(
            endpoint=settings.MINIO_HOST,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
        )
        if not self.client.bucket_exists(settings.MINIO_BUCKET_NAME):
            self.client.make_bucket(settings.MINIO_BUCKET_NAME)

    def save(self, file: UploadFile, prefix: str = "") -> str:
        """Saves file and returns path to it (join(root, generated_filename))

        Params:
            file (UploadFile): file
        Returns:
            str: filename of created file inside bucket
        Raises:
            INCOMPLETE_FILE_SENT: if file.content_type or file.size is None
        """
        if file.content_type is None or file.size is None:
            raise responses.INCOMPLETE_FILE_SENT.exception()
        uuid = uuid4()
        filename = f"{prefix}{uuid.hex}"
        extension = guess_extension(file.content_type.split(";")[0].strip())
        if extension is not None:
            filename += extension
        self.client.put_object(
            bucket_name=settings.MINIO_BUCKET_NAME,
            content_type=file.content_type,
            object_name=filename,
            data=file.file,
            length=file.size,
        )
        return filename

    def remove(self, filename: str) -> None:
        self.client.remove_object(settings.MINIO_BUCKET_NAME, filename)

    def remove_relative(self, filename: str) -> None:
        self.remove(filename)

    def exists(self, filename: str) -> bool:
        try:
            self.client.stat_object(settings.MINIO_BUCKET_NAME, filename)
            return True
        except S3Error:
            return False

    def exists_relative(self, filename) -> bool:
        return self.exists(filename)

    def clear_unlinked(self, prefix: str, white_list: list[str]) -> None:
        for obj in self.client.list_objects(
            bucket_name=settings.MINIO_BUCKET_NAME, prefix=prefix
        ):
            if obj.object_name is not None and obj.object_name not in white_list:
                self.client.remove_object(settings.MINIO_BUCKET_NAME, obj.object_name)


def multipart_form_data(content_type: str = Header(...)):
    """Force request MIME-type to multipart/form-data"""

    if content_type != "multipart/form-data":
        raise HTTPException(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Unsupported media type: {content_type}."
            " It must be multipart/form-data",
        )
