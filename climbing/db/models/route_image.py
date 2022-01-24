from datetime import datetime, timezone
from typing import TYPE_CHECKING
from uuid import uuid4

from fastapi_users_db_sqlalchemy import UUID4
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .route import Route


class BaseRouteImage(SQLModel):
    url: str


class RouteImage(BaseRouteImage, table=True):
    id: UUID4 = Field(default_factory=uuid4, primary_key=True)
    url: str = Field(max_length=300)
    route_id: UUID4 = Field(foreign_key="route.id")
    route: "Route" = Relationship(back_populates="images")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
