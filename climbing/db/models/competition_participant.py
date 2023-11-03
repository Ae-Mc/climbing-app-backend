from typing import TYPE_CHECKING
from uuid import uuid4

from pydantic import UUID4
from sqlalchemy import Column, ForeignKey, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

from climbing.db.models.user import User

if TYPE_CHECKING:
    from .competition import Competition


class CompetitionParticipantBase(SQLModel):
    """Базовая модель участника соревнований"""

    place: int = Field(..., title="Место, занятое участником в соревновании")


class CompetitionParticipantCreateWithCompetition(CompetitionParticipantBase):
    """Модель добавления участника соревнований"""

    user_id: UUID4 = Field(
        ..., title="ID участника (пользователя)", foreign_key="user.id"
    )


class CompetitionParticipantCreate(CompetitionParticipantBase):
    """Модель добавления участника соревнований"""

    competition_id: UUID4 = Field(..., title="ID соревнования")
    user_id: UUID4 = Field(..., title="ID участника (пользователя)")


class CompetitionParticipantUpdate(CompetitionParticipantCreate):
    """Модель обновления участника соревнований"""

    id: UUID4 = Field(default_factory=uuid4, title="ID отношения")


class CompetitionParticipant(CompetitionParticipantCreate, table=True):
    """Таблица-отношение между соревнованиями и пользователями"""

    __table_args__ = (
        UniqueConstraint(
            "competition_id",
            "user_id",
            name="competitionparticipant_unique_constraint",
        ),
    )

    id: UUID4 = Field(
        default_factory=uuid4, title="ID отношения", primary_key=True
    )
    competition: "Competition" = Relationship(back_populates="participants")
    competition_id: UUID4 = Field(
        ...,
        title="ID соревнования",
        sa_column=Column(
            ForeignKey(
                "competition.id",
                ondelete="CASCADE",
                name="competitionparticipant_competition_fk",
            ),
            nullable=False,
        ),
    )
    user: User = Relationship()
    user_id: UUID4 = Field(
        ...,
        title="ID участника (пользователя)",
        sa_column=Column(
            ForeignKey(
                "user.id",
                ondelete="CASCADE",
                name="competitionparticipant_user_fk",
            ),
            nullable=False,
        ),
    )
