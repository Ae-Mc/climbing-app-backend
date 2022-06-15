from datetime import timedelta

from pydantic import BaseModel, Field

from climbing.schemas.ascent import AscentReadWithAll


class ExpiringAscent(BaseModel):
    """Схема для предоставления информации об оставшемся времени до
    исчезновения трассы из рейтинга"""

    ascent: AscentReadWithAll = Field(..., title="Подьём")
    time_to_expire: timedelta = Field(
        ..., title="Время до исчезновения из рейтинга"
    )
