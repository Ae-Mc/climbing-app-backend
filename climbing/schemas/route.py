from datetime import date

from fastapi import UploadFile

from pydantic import Field

from .category import Category
from .image import Image
from .multipart_form_data_compatible_model import (
    MultipartFormDataCompatibleModel,
)
from .user import User


class RouteBase(MultipartFormDataCompatibleModel):
    """Модель для хранения информации о трассе."""

    name: str = Field(
        ..., min_length=1, max_length=150, title="Название трассы"
    )
    category: Category = Field(..., title="Категория трассы")
    mark_color: str = Field(
        ..., min_length=4, max_length=100, title="Цвет меток трассы"
    )
    author: str | None = Field(
        None, min_length=0, max_length=150, title="Автор трассы"
    )
    description: str = Field(..., title="Описание трассы")
    creation_date: date = Field(..., title="Дата создания (постановки) трассы")


class RouteCreate(RouteBase):
    """Модель для создания трассы. Должна создаваться вручную (не может быть
    использована напрямую как параметр запроса)."""

    images: list[UploadFile] = Field(...)


class RouteUpdate(RouteBase):
    """Модель для обновления трассы. Должна создаваться вручную (не может быть
    использована напрямую как параметр запроса)."""

    images: list[UploadFile] = Field(...)


class Route(RouteBase):
    """Модель для хранения информации о трассе."""

    uploader: User = Field(..., title="Пользователь, загрузивший трассу")
    images: list[Image] = Field([], title="Список изображений трассы")

    class Config:
        """Standard Config class from FastAPI"""

        orm_mode = True

    id: int = Field(..., ge=1, title="ID трассы")
