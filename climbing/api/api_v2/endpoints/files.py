from uuid import uuid4

from fastapi import APIRouter, Depends, UploadFile
from fastapi_versionizer import api_version
from minio import Minio

from climbing.core import responses
from climbing.core.config import settings
from climbing.core.security import current_user

router = APIRouter()


@api_version(2)
@router.post(
    "",
    description="Возвращает путь к файлу на файловом сервере",
    dependencies=[Depends(current_user)],
    responses={
        **responses.INCOMPLETE_FILE_SENT.docs(),
    },
)
async def add_file(file: UploadFile) -> str:
    if file.content_type is None or file.size is None:
        raise responses.INCOMPLETE_FILE_SENT.exception()
    client = Minio(
        endpoint=settings.MINIO_HOST,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=False,
        cert_check=False,
    )
    uuid = uuid4()
    filename = "routes_images/" + uuid.hex
    if not client.bucket_exists(settings.MINIO_BUCKET_NAME):
        client.make_bucket(settings.MINIO_BUCKET_NAME)
    client.put_object(
        bucket_name=settings.MINIO_BUCKET_NAME,
        content_type=file.content_type,
        object_name=filename,
        data=file.file,
        length=file.size,
    )
    return f"{settings.MINIO_BUCKET_NAME}/{filename}"
