from typing import List

from pydantic import BaseModel, Field

from climbing.schemas.ascent import AscentReadWithAll
from climbing.schemas.base_read_classes import UserRead
from climbing.schemas.competition_participant import (
    CompetitionParticipantReadWithAll,
)


class Score(BaseModel):
    """Модель для отображения рейтинга"""

    user: UserRead = Field(..., title="Пользователь")
    score: float = Field(..., title="Количество очков")
    ascents: List[AscentReadWithAll] = Field(..., title="Пять лучших подъёмов")
    participations: List[CompetitionParticipantReadWithAll] = Field(
        [], title="Участия в соревнованиях"
    )
