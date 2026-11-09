import logging
import time
from datetime import datetime
from typing import Sequence

from fastapi import APIRouter, Depends, Path, Query, Request
from fastapi_users.exceptions import UserNotExists
from fastapi_versionizer import api_version
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from climbing.core import responses
from climbing.core.security import optional_user
from climbing.core.tourist_visibility import (
    may_view_tourists,
    rating_tourist_filter,
)
from climbing.core.user_manager import UserManager, get_user_manager
from climbing.db.models.user import User
from climbing.db.session import get_async_session
from climbing.schemas.ascent import AscentReadRatingWithRoute
from climbing.schemas.filters.rating_filter import RatingFilter
from climbing.util.rating_calculator import RatingCalculator

router = APIRouter()


@api_version(2)
@router.get("/user/{user_id}/ascents", responses=responses.ID_NOT_FOUND.docs())
async def ascents(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
    start_date: datetime | None = Query(None),
    end_date: datetime | None = Query(None),
    user_id: UUID4 = Path(),
    viewer: User | None = Depends(optional_user),
    user_manager: UserManager = Depends(get_user_manager),
) -> Sequence[AscentReadRatingWithRoute]:
    try:
        target = await user_manager.get(user_id)
    except UserNotExists:
        raise responses.ID_NOT_FOUND.exception()
    if target.is_tourist and not may_view_tourists(viewer):
        raise responses.ID_NOT_FOUND.exception()
    start = time.time()
    calc = RatingCalculator(
        session=session,
        filter_params=RatingFilter(is_tourist=rating_tourist_filter(viewer)),
    )
    if end_date is None:
        end_date = datetime.now()
    calc.set_date_range(start_date=start_date, end_date=end_date)
    result = await calc.get_user_rating_ascents(user_id, request)
    logging.debug(result)
    end = time.time()
    logging.info(f"Ascent getting for user {user_id} time: {start - end}")
    return result
