from typing import List

from pydantic import Field

from climbing.schemas.base_read_classes import CompetitionRead, UserRead
from climbing.schemas.competition_participant import (
    CompetitionParticipantReadWithUser,
)


class CompetitionReadWithParticipants(CompetitionRead):
    participants: List[CompetitionParticipantReadWithUser] = Field(
        title="Участники соревнования"
    )


class CompetitionReadWithOrganizer(CompetitionRead):
    organizer: UserRead = Field(title="Организатор соревнования")


class CompetitionReadWithAll(
    CompetitionReadWithOrganizer, CompetitionReadWithParticipants
):
    pass
