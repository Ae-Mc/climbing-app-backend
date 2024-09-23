from datetime import datetime, timezone
from typing import TYPE_CHECKING
from uuid import uuid4

from fastapi import Request
from pydantic import UUID4
from sqlmodel import Field, Relationship, SQLModel

from climbing.core.config import settings

if TYPE_CHECKING:
    from .route import Route


class BaseRouteImage(SQLModel):
    """Базовая модель для хранения изображений трасс"""

    url: str

    def set_absolute_url(self, request: Request):
        """Устанавливает абсолютный, а не относительный URL-адрес для
        изображения"""
        if "://" in self.url:
            return
        url_obj = request.url
        self.url = f"{url_obj.scheme}://{settings.MINIO_HOST}/{settings.MINIO_BUCKET_NAME}/{self.url}"


class RouteImage(BaseRouteImage, table=True):
    """Полная таблица для хранения изображений трасс"""

    id: UUID4 = Field(default_factory=uuid4, primary_key=True)
    url: str = Field(max_length=300)
    route_id: UUID4 = Field(foreign_key="route.id")
    route: "Route" = Relationship(back_populates="images")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
