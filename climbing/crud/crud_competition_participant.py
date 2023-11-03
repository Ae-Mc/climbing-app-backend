from fastapi_users_db_sqlmodel import AsyncSession

from climbing.crud.base import CRUDBase
from climbing.db.models.competition_participant import (
    CompetitionParticipant,
    CompetitionParticipantCreate,
    CompetitionParticipantUpdate,
)


class CRUDCompetitionParticipant(
    CRUDBase[
        CompetitionParticipant,
        CompetitionParticipantCreate,
        CompetitionParticipantUpdate,
    ]
):
    """CRUD class for competition participations"""


competition_participant = CRUDCompetitionParticipant(CompetitionParticipant)
