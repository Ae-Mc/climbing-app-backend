from typing import Type

from fastapi_users_db_sqlmodel import AsyncSession
from pydantic import UUID4
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from climbing.db.models import Ascent, AscentCreate, AscentUpdate

from .base import CRUDBase


class CRUDAscent(CRUDBase[Ascent, AscentCreate, AscentUpdate]):
    """CRUD class for ascent models"""

    def __init__(self, model: Type[Ascent] = Ascent) -> None:
        super().__init__(model)

    async def get(self, session: AsyncSession, row_id: UUID4) -> Ascent | None:
        return (
            await session.execute(
                select(Ascent)
                .options(selectinload("route"))
                .options(selectinload("route.author"))
                .options(selectinload("route.images"))
                .options(selectinload("user"))
                .where(Ascent.id == row_id)
            )
        ).scalar_one_or_none()

    async def get_all(self, session: AsyncSession) -> list[Ascent]:
        return (
            (
                await session.execute(
                    select(Ascent)
                    .options(selectinload("route"))
                    .options(selectinload("route.author"))
                    .options(selectinload("route.images"))
                    .options(selectinload("user"))
                )
            )
            .scalars()
            .all()
        )

    async def get_for_user(
        self, session: AsyncSession, user_id: UUID4
    ) -> list[Ascent]:
        """Получение списка подъёмов для конкретного пользователя"""
        return (
            (
                await session.execute(
                    select(Ascent)
                    .options(selectinload("route"))
                    .options(selectinload("route.author"))
                    .options(selectinload("route.images"))
                    .options(selectinload("user"))
                    .where(Ascent.user_id == user_id)
                )
            )
            .scalars()
            .all()
        )

    async def create(
        self, session: AsyncSession, entity: AscentCreate
    ) -> Ascent:
        ascent_instance = self.model(**entity.dict())
        session.add(ascent_instance)
        await session.commit()
        return await self.get(session, ascent_instance.id)


ascent = CRUDAscent()
