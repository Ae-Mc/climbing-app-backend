from datetime import date as dateclass
from datetime import datetime, timezone
from typing import List
from uuid import uuid4

from pydantic import UUID4
from sqlmodel import Field, Relationship, SQLModel

from climbing.db.models.competition_participant import (
    CompetitionParticipant,
    CompetitionParticipantCreateWithCompetition,
)
from climbing.db.models.user import User


class CompetitionBase(SQLModel):
    """Базовый класс таблицы соревнований"""

    name: str = Field(..., title="Название соревнования")
    date: dateclass = Field(..., title="Дата проведения соревнования")
    ratio: float = Field(..., title="Коэффицент для баллов рейтинга")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        title="Дата добавления соревнования на сервер",
    )


class CompetitionCreate(CompetitionBase):
    """Класс для создания соревнования"""

    organizer_id: UUID4 = Field(..., title="ID организатора соревнования")
    participants: List[CompetitionParticipantCreateWithCompetition] = Field(
        [], title="Участники соревнования"
    )


class CompetitionUpdate(CompetitionBase):
    """Класс для обновления соревнования"""

    organizer_id: UUID4 = Field(..., title="ID организатора соревнования")


class Competition(CompetitionBase, table=True):
    """Таблица для хранения соревнований"""

    id: UUID4 = Field(title="ID соревнования", primary_key=True, default_factory=uuid4)
    organizer_id: UUID4 = Field(
        ..., title="ID организатора соревнования", foreign_key="user.id"
    )
    organizer: User = Relationship()
    participants: list[CompetitionParticipant] = Relationship(
        back_populates="competition",
        # Instruct the ORM how to track changes to local objects
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
