from typing import Sequence

from pydantic import UUID4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import col

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


class CRUDCompetition(CRUDBase[Competition, CompetitionCreate, CompetitionUpdate]):
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
                .where(col(CompetitionParticipant.id) == db_entity.id)
                .options(
                    selectinload(CompetitionParticipant.competition),
                    selectinload(CompetitionParticipant.user),
                )
            )
        ).scalar_one()

    async def create(
        self, session: AsyncSession, entity: CompetitionCreate
    ) -> Competition:
        db_entity = self.model(**entity.model_dump(exclude={"participants": True}))
        db_entity.participants = list(
            map(
                lambda x: CompetitionParticipant(
                    place=x.place,
                    user_id=x.user_id,
                    competition_id=db_entity.id,
                ),
                entity.participants,
            )
        )
        session.add(db_entity)
        await session.commit()
        result = await self.get(session, db_entity.id)
        assert result is not None
        return result

    async def get_for_organizer(
        self, session: AsyncSession, user_id: UUID4
    ) -> Sequence[Competition]:
        query = (
            select(Competition)
            .options(
                selectinload(col(Competition.participants)).selectinload(  # type: ignore
                    CompetitionParticipant.user
                ),
                selectinload(Competition.organizer),
            )
            .where(col(Competition.organizer_id) == user_id)
        )
        return (await session.execute(query)).scalars().all()


competition = CRUDCompetition(Competition)
