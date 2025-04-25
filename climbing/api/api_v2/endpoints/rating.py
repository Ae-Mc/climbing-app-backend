import logging
import time
from datetime import datetime
from typing import Sequence

from fastapi import APIRouter, Depends, Path, Query, Request
from fastapi_versionizer import api_version
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from climbing.db.session import get_async_session
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
) -> Sequence[AscentReadRatingWithRoute]:
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
