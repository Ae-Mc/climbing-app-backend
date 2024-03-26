from datetime import datetime

from pydantic import UUID4, BaseModel, Field

from climbing.schemas.filters.order_enum import Order


class AscentsFilter(BaseModel):
    date_from: datetime | None = Field(default=None)
    is_flash: bool | None = Field(default=None)
    route_id: UUID4 | None = Field(default=None)
    user_id: UUID4 | None = Field(default=None)
    sort_by_date: Order | None = Field(default=None)
