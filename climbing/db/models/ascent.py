from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from fastapi_users_db_sqlmodel import Field
from pydantic import UUID4
from sqlalchemy import Column, ForeignKey, String
from sqlmodel import Relationship, SQLModel

from .route import Route

if TYPE_CHECKING:
    from .user import User


class AscentBase(SQLModel):
    is_flash: bool = Field()
    date: datetime = Field()


class AscentCreate(AscentBase):
    user_id: UUID4 = Field()
    route_id: UUID4 = Field()


class AscentUpdate(AscentBase):
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
    route: "Route" = Relationship()
    user_id: UUID4 = Field(
        # foreign_key="user.id"
        sa_column=Column(
            ForeignKey("user.id", ondelete="CASCADE", name="ascent_user_fk"),
            nullable=False,
        ),
    )
    user: "User" = Relationship(back_populates="ascents")
