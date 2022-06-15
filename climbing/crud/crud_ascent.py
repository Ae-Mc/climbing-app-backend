from datetime import datetime

from fastapi_users_db_sqlmodel import AsyncSession
from pydantic import UUID4
from sqlalchemy.future import select

from climbing.db.models import Ascent, AscentCreate, AscentUpdate

from .base import CRUDBase


class CRUDAscent(CRUDBase[Ascent, AscentCreate, AscentUpdate]):
    """CRUD class for ascent models"""

    async def get_for_user(
        self,
        session: AsyncSession,
        user_id: UUID4,
        from_date: datetime = None,
        to_date: datetime = None,
    ) -> list[Ascent]:
        """Получение списка подъёмов для конкретного пользователя за
        определённый период. Если период на задан, то за всё время"""
        statement = (
            select(Ascent)
            .options(*self.select_options)
            .where(Ascent.user_id == user_id)
        )
        if from_date is not None:
            statement = statement.where(Ascent.date >= from_date)
        if to_date is not None:
            statement = statement.where(Ascent.date <= to_date)

        return (await session.execute(statement)).scalars().all()


ascent = CRUDAscent(Ascent)
