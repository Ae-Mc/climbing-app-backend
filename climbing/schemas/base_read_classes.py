from datetime import datetime

from fastapi_users_db_sqlmodel import Field
from pydantic import UUID4

from climbing.db.models import AscentBase, RouteBaseDB, UserBaseWithCreatedAt
from climbing.db.models.competition import CompetitionBase
from climbing.db.models.competition_participant import (
    CompetitionParticipantBase,
)


class UserRead(UserBaseWithCreatedAt):
    """User returning pydantic scheme"""

    id: UUID4
    email: str
    is_superuser: bool


class RouteRead(RouteBaseDB):
    """Базовая модель для чтения трассы"""

    id: UUID4 = Field(title="ID трассы")
    created_at: datetime = Field(title="Дата добавления трассы на сервер")


class AscentRead(AscentBase):
    """Базовая модель для чтения прохождения трассы"""

    id: UUID4 = Field(title="ID прохождения")


class CompetitionParticipantRead(CompetitionParticipantBase):
    """Базовая модель для чтения участника соревнования"""

    id: UUID4 = Field(title="ID записи")


class CompetitionRead(CompetitionBase):
    """Схема для чтения соревнования"""

    id: UUID4 = Field(title="ID записи")
