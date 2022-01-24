from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .route import Route


class BaseRouteImage(SQLModel):
    url: str


class RouteImage(BaseRouteImage, table=True):
    id: int | None = Field(default=None, primary_key=True)
    url: str = Field(max_length=300)
    route_id: int = Field(foreign_key="route.id")
    route: "Route" = Relationship(back_populates="images")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
