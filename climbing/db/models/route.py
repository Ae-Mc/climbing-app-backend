import json
from datetime import date, datetime, timezone
from typing import List
from uuid import uuid4

from fastapi import Request, UploadFile
from pydantic import UUID4, model_validator, validator
from sqlmodel import AutoString, Field, Relationship, SQLModel

from .category import Category
from .route_image import RouteImage
from .user import User


class RouteBase(SQLModel):
    """Модель для хранения информации о трассе."""

    name: str = Field(..., min_length=1, max_length=150, title="Название трассы")
    category: Category = Field(..., title="Категория трассы", sa_type=AutoString)
    mark_color: str = Field(
        ..., min_length=4, max_length=100, title="Цвет меток трассы"
    )
    description: str = Field(..., title="Описание трассы")
    creation_date: date = Field(..., title="Дата создания (постановки) трассы")
    archived: bool = Field(
        default=False,
        title="Устарела ли трасса (архивная ли она)",
        sa_column_kwargs={"server_default": "0"},
    )

    @model_validator(mode="before")
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value


class RouteBaseDB(RouteBase):
    author_id: UUID4 = Field(..., title="ID автора трассы", foreign_key="user.id")


class RouteCreate(RouteBase):
    """Модель для создания трассы. Должна создаваться вручную (не может быть
    использована напрямую как параметр запроса)."""

    images: list[UploadFile] = Field(...)
    author_id: UUID4 = Field(description="ID автора трассы")

    @validator("images", each_item=True)
    @classmethod
    def validate_image(cls, image: UploadFile):
        """Проверяет, что каждое изображение имеет MIME-тип image"""

        if image.content_type is None:
            if image.filename is None:
                is_image = False
            else:
                is_image = image.filename.endswith(".jpg") or image.filename.endswith(
                    ".png"
                )
        else:
            is_image = image.content_type.split("/")[0] == "image"

        if not is_image:
            raise ValueError("Must have MIME-type image/*")
        return image


class RouteUpdate(RouteCreate):
    """Модель для обновления трассы. Должна создаваться вручную (не может быть
    использована напрямую как параметр запроса)."""


class Route(RouteBaseDB, table=True):
    """Модель для хранения информации о трассе."""

    id: UUID4 = Field(title="ID трассы", primary_key=True, default_factory=uuid4)
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
