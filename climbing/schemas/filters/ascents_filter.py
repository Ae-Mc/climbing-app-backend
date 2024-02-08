from datetime import datetime

from pydantic import UUID4, BaseModel, Field

from climbing.schemas.filters.order_enum import Order


class AscentsFilter(BaseModel):
    date_from: datetime | None = Field(None)
    is_flash: bool | None = Field(None)
    route_id: UUID4 | None = Field(None)
    user_id: UUID4 | None = Field(None)
    sort_by_date: Order | None = Field(None)
