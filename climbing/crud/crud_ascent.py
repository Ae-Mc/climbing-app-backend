from fastapi_users_db_sqlmodel import AsyncSession
from pydantic import UUID4
from sqlalchemy.future import select

from climbing.db.models import Ascent, AscentCreate, AscentUpdate

from .base import CRUDBase


class CRUDAscent(CRUDBase[Ascent, AscentCreate, AscentUpdate]):
    """CRUD class for ascent models"""

    async def get_for_user(
        self, session: AsyncSession, user_id: UUID4
    ) -> list[Ascent]:
        """Получение списка подъёмов для конкретного пользователя"""
        return (
            (
                await session.execute(
                    select(Ascent)
                    .options(*self.select_options)
                    .where(Ascent.user_id == user_id)
                )
            )
            .scalars()
            .all()
        )


ascent = CRUDAscent(Ascent)
