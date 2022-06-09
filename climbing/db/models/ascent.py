from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from fastapi import Request
from pydantic import UUID4
from sqlalchemy import Column, ForeignKey
from sqlmodel import Field, Relationship, SQLModel

from .route import Route

if TYPE_CHECKING:
    from .user import User


class AscentBase(SQLModel):
    """Базовая модель подъёма"""

    is_flash: bool = Field(..., title="Пройдена ли трасса с первой попытки")
    date: datetime = Field(..., title="Дата подъёма")


class AscentCreate(AscentBase):
    """Модель для добавления подъёма"""

    user_id: UUID4 = Field()
    route_id: UUID4 = Field()


class AscentUpdate(AscentBase):
    """Модель для обновления подъёма"""

    user_id: UUID4 = Field()
    route_id: UUID4 = Field()


class Ascent(AscentBase, table=True):
    """Ascent model"""

    id: UUID4 = Field(default_factory=uuid4, primary_key=True)
    route_id: UUID4 = Field(
        sa_column=Column(
            ForeignKey("route.id", ondelete="CASCADE", name="ascent_route_fk"),
            nullable=False,
        )
    )
    route: Route = Relationship()
    user_id: UUID4 = Field(
        # foreign_key="user.id"
        sa_column=Column(
            ForeignKey("user.id", ondelete="CASCADE", name="ascent_user_fk"),
            nullable=False,
        ),
    )
    user: "User" = Relationship(back_populates="ascents")

    def set_absolute_image_urls(self, request: Request) -> None:
        """Устанавливает абсолютные, а не относительные URL-адреса для
        изображений"""
        # pylint: disable=no-member
        self.route.set_absolute_image_urls(request)
