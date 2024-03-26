from typing import List

from pydantic import BaseModel, ConfigDict, Field

from climbing.schemas.ascent import AscentReadWithRoute
from climbing.schemas.base_read_classes import UserRead
from climbing.schemas.competition_participant import (
    CompetitionParticipantReadRating,
)


class Score(BaseModel):
    """Модель для отображения рейтинга"""

    user: UserRead = Field(..., title="Пользователь")
    place: int = Field(..., title="Место в рейтинге")
    score: float = Field(default=0, title="Количество очков")
    ascents_score: float = Field(
        default=0,
        title="Количество очков за трассы",
        description="По этому параметру строится соревнование, за которое"
        " зачисляются очки рейтинга по стандартной схеме",
    )
    participations: List[CompetitionParticipantReadRating] = Field(
        default_factory=lambda: list(), title="Участия в соревнованиях"
    )
    ascents: List[AscentReadWithRoute] = Field(
        default_factory=lambda: list(), title="Список пролазов"
    )

    model_config = ConfigDict(from_attributes=True)
