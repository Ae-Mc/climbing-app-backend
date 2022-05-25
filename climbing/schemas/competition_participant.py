from pydantic import UUID4, Field

from climbing.db.models.competition_participant import (
    CompetitionParticipantBase,
)
from climbing.schemas.base_read_classes import (
    CompetitionParticipantRead,
    CompetitionRead,
    UserRead,
)


class CompetitionParticipantReadWithUser(CompetitionParticipantRead):
    user: UserRead = Field(title="Участник")


class CompetitionParticipantReadWithCompetition(CompetitionParticipantRead):
    competition: CompetitionRead = Field(title="Соревнование")


class CompetitionParticipantReadWithAll(
    CompetitionParticipantReadWithCompetition,
    CompetitionParticipantReadWithUser,
):
    pass


class CompetitionParticipantCreateScheme(CompetitionParticipantBase):
    user_id: UUID4 = Field(title="ID участника")
