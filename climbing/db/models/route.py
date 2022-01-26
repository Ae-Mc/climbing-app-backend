from datetime import date, datetime, timezone
from typing import List
from uuid import uuid4

from fastapi import UploadFile
from pydantic import UUID4, validator
from sqlmodel import Field, Relationship, SQLModel

from .category import Category
from .route_image import RouteImage
from .user import User, UserScheme


class RouteBase(SQLModel):
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
    uploader: User = Field(..., title="Пользователь, загрузивший трассу")

    @validator("images", each_item=True)
    @classmethod
    def validate_image(cls, image: UploadFile):
        if image.content_type.split("/")[0] != "image":
            raise ValueError("Must have MIME-type image/*")
        return image


class RouteUpdate(RouteBase):
    """Модель для обновления трассы. Должна создаваться вручную (не может быть
    использована напрямую как параметр запроса)."""

    images: list[UploadFile] | None = Field(None)


class Route(RouteBase, table=True):
    """Модель для хранения информации о трассе."""

    id: UUID4 = Field(
        title="ID трассы", primary_key=True, default_factory=uuid4
    )
    uploader_id: UUID4 = Field(
        ..., title="ID пользователя, загрузивший трассу", foreign_key="user.id"
    )
    uploader: User = Relationship()
    images: List[RouteImage] = Relationship(back_populates="route")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        title="Дата добавления трассы на сервер",
    )


class RouteRead(RouteBase):
    id: UUID4 = Field(title="ID трассы")
    uploader: UserScheme
    images: List[RouteImage] = []
    created_at: datetime = Field(title="Дата добавления трассы на сервер")
