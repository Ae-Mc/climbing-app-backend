import logging
import time
from datetime import datetime
from typing import Sequence

from fastapi import APIRouter, Depends, Path, Query, Request
from fastapi_versionizer import api_version
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from climbing.db.session import get_async_session
from climbing.core.security import fastapi_users
from climbing.db.models.user import User
from sqlalchemy import select
from fastapi import HTTPException
from climbing.schemas.ascent import AscentReadRatingWithRoute
from climbing.util.rating_calculator import RatingCalculator

router = APIRouter()


@api_version(2)
@router.get("/user/{user_id}/ascents")
async def ascents(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
    start_date: datetime | None = Query(None),
    end_date: datetime | None = Query(None),
    user_id: UUID4 = Path(),
    viewer: User | None = Depends(fastapi_users.current_user(optional=True)),
) -> Sequence[AscentReadRatingWithRoute]:
    target = await session.scalar(select(User).where(User.id == user_id))
    if target is None or (target.is_tourist and not (viewer and viewer.is_tourist)):
        raise HTTPException(status_code=404)
    start = time.time()
    calc = RatingCalculator(session=session)
    if end_date is None:
        end_date = datetime.now()
    calc.set_date_range(start_date=start_date, end_date=end_date)
    result = await calc.get_user_rating_ascents(user_id, request)
    logging.debug(result)
    end = time.time()
    logging.info(f"Ascent getting for user {user_id} time: {start - end}")
    return result
