from typing import List

from pydantic import BaseModel, Field

from climbing.schemas.base_read_classes import UserRead
from climbing.schemas.competition_participant import (
    CompetitionParticipantReadWithAll,
)


class Score(BaseModel):
    """Модель для отображения рейтинга"""

    user: UserRead = Field(..., title="Пользователь")
    score: float = Field(0, title="Количество очков")
    ascents_score: float = Field(
        0,
        title="Количество очков за трассы",
        description="По этому параметру строится соревнование, за которое"
        " зачисляются очки рейтинга по стандартной схеме",
    )
    participations: List[CompetitionParticipantReadWithAll] = Field(
        [], title="Участия в соревнованиях"
    )
