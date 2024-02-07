from datetime import date, datetime, timezone
from typing import List
from uuid import uuid4

from fastapi import Request, UploadFile
from pydantic import UUID4, validator
from sqlmodel import Field, Relationship, SQLModel

from .category import Category
from .route_image import RouteImage
from .user import User


class RouteBase(SQLModel):
    """Модель для хранения информации о трассе."""

    name: str = Field(
        ..., min_length=1, max_length=150, title="Название трассы"
    )
    category: Category = Field(..., title="Категория трассы")
    mark_color: str = Field(
        ..., min_length=4, max_length=100, title="Цвет меток трассы"
    )
    description: str = Field(..., title="Описание трассы")
    creation_date: date = Field(..., title="Дата создания (постановки) трассы")
    author_id: UUID4 = Field(
        ..., title="ID автора трассы", foreign_key="user.id"
    )
    archived: bool = Field(False, sa_column_kwargs={"server_default": "0"})


class RouteCreate(RouteBase):
    """Модель для создания трассы. Должна создаваться вручную (не может быть
    использована напрямую как параметр запроса)."""

    images: list[UploadFile] = Field(...)
    author: User = Field(..., title="Автор трассы")
    author_id: UUID4 | None = Field(None)

    @validator("images", each_item=True)
    @classmethod
    def validate_image(cls, image: UploadFile):
        """Проверяет, что каждое изображение имеет MIME-тип image"""

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
    author: User = Relationship()
    images: List[RouteImage] = Relationship(back_populates="route")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        title="Дата добавления трассы на сервер",
    )

    def set_absolute_image_urls(self, request: Request) -> None:
        """Устанавливает абсолютные, а не относительные URL-адреса для
        изображений"""

        for image in self.images:  # pylint: disable=not-an-iterable
            image.set_absolute_url(request)
