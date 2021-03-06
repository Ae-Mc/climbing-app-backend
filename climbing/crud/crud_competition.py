from fastapi_users_db_sqlmodel import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from climbing.crud.base import CRUDBase
from climbing.db.models.competition import (
    Competition,
    CompetitionCreate,
    CompetitionUpdate,
)
from climbing.db.models.competition_participant import (
    CompetitionParticipant,
    CompetitionParticipantCreate,
)


class CRUDCompetition(
    CRUDBase[Competition, CompetitionCreate, CompetitionUpdate]
):
    """CRUD class for competition models"""

    async def add_participant(
        self, session: AsyncSession, entity: CompetitionParticipantCreate
    ) -> CompetitionParticipant:
        """Add participant to existing competition"""
        db_entity = CompetitionParticipant(**entity.dict())
        session.add(db_entity)
        await session.commit()
        return (
            await session.execute(
                select(CompetitionParticipant)
                .where(CompetitionParticipant.id == db_entity.id)
                .options(
                    selectinload(CompetitionParticipant.competition),
                    selectinload(CompetitionParticipant.user),
                )
            )
        ).scalar_one()

    async def create(
        self, session: AsyncSession, entity: CompetitionCreate
    ) -> Competition:
        db_entity = self.model(**entity.dict(exclude={"participants": True}))
        db_entity.participants = list(
            map(
                lambda x: CompetitionParticipant(
                    place=x.place, competition=db_entity, user_id=x.user_id
                ),
                entity.participants,
            )
        )
        session.add(db_entity)
        await session.commit()
        return await self.get(session, db_entity.id)


competition = CRUDCompetition(Competition)
