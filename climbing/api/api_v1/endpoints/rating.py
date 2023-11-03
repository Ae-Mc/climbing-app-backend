from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from climbing.core.score_maps import category_to_score_map, place_to_score_map
from climbing.db.session import get_async_session
from climbing.schemas.category_to_score import CategoryToScore
from climbing.schemas.rating_filter import RatingFilter
from climbing.schemas.score import Score
from climbing.util.rating_calculator import RatingCalculator

router = APIRouter()


@router.get(
    "",
    name="rating:rating",
    response_model=List[Score],
)
async def rating(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
    start_date: datetime | None = Query(None),
    end_date: datetime | None = Query(None),
    is_student: bool | None = Query(None),
) -> List[Score]:
    """Получение подъёмов за последнии полтора месяца для рейтинга"""

    if end_date is None:
        end_date = datetime.now()

    calc = RatingCalculator(session=session)
    calc.set_date_range(end_date=end_date, start_date=start_date)
    if is_student is not None:
        calc.filter = RatingFilter(is_student=is_student)
    await calc.fill_ascents(request=request)
    await calc.calc_routes_competition()
    await calc.fill_other_competition_scores()
    calc.fill_routes_competition_scores()
    return calc.scores


@router.get("/category_score_map", response_model=list[CategoryToScore])
def category_score_map():
    """Список оценок трасс"""
    return [
        CategoryToScore(category=category, score=score)
        for category, score in category_to_score_map.items()
    ]


class PlaceToScore(BaseModel):
    """Модель для описания цены места"""

    place: int = Field(..., title="Место")
    score: float = Field(..., title="Количество очков за место")


@router.get("/competition_score_map", response_model=list[PlaceToScore])
def competition_score_map():
    """Список оценок мест в соревнованиях"""
    return [
        PlaceToScore(place=place, score=score)
        for place, score in place_to_score_map.items()
    ]
