from datetime import datetime

from dateutil.relativedelta import relativedelta
from fastapi import APIRouter, Depends, Query, Request
from fastapi_users_db_sqlmodel import AsyncSession, selectinload
from pydantic import BaseModel, Field
from sqlalchemy import case, desc, select

from climbing.core.category_to_score_map import category_to_score_map
from climbing.db.models.ascent import Ascent
from climbing.db.models.category import Category
from climbing.db.models.route import Route
from climbing.db.models.user import User
from climbing.db.session import get_async_session
from climbing.schemas.score import Score

router = APIRouter()


@router.get(
    "",
    name="rating:rating",
    response_model=list[Score],
)
async def rating(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
    start_date: datetime = Query(None),
    end_date: datetime = Query(None),
):
    """Получение подъёмов за последнии полтора месяца для рейтинга"""

    if end_date is None:
        end_date = datetime.now()
    end_date = end_date.date() + relativedelta(
        hours=23, minutes=59, seconds=59
    )

    if start_date is None:
        start_date = end_date + relativedelta(months=-1, days=-15)
    start_date = start_date.date()

    whens = {
        category: index for index, category in enumerate(Category.values())
    }

    _ascents: list[Ascent] = (
        (
            await session.execute(
                select(Ascent)
                .where(Ascent.date >= start_date)
                .where(Ascent.date <= end_date)
                .group_by(Ascent.user_id, Ascent.route_id)
                .options(selectinload("route"))
                .options(selectinload("route.author"))
                .options(selectinload("route.images"))
                .options(selectinload("user"))
                .join(Route, onclause=Ascent.route_id == Route.id)
                .order_by(desc(case(value=Route.category, whens=whens)))
            )
        )
        .scalars()
        .all()
    )

    ascents_per_user: dict[User, list[Ascent]] = {}

    for _ascent in _ascents:
        _ascent.set_absolute_image_urls(request)
        if _ascent.user not in ascents_per_user:
            ascents_per_user[_ascent.user] = []
        if len(ascents_per_user[_ascent.user]) < 5:
            ascents_per_user[_ascent.user].append(_ascent)

    return sorted(
        [
            Score(
                user=user,
                ascents=_ascents,
                score=sum(
                    map(
                        lambda _ascent: category_to_score_map[
                            _ascent.route.category
                        ],
                        _ascents,
                    )
                ),
            )
            for user, _ascents in ascents_per_user.items()
        ],
        key=lambda score: score.score,
        reverse=True,
    )


class CategoryToScore(BaseModel):
    """Модель для описания цены категории"""

    category: Category = Field(..., title="Категория")
    score: float = Field(..., title="Количество очков за прохождение")


@router.get("/score_map", response_model=list[CategoryToScore])
def score_map():
    """Список оценок трасс"""
    return list(
        map(
            lambda item: CategoryToScore(category=item[0], score=item[1]),
            category_to_score_map.items(),
        )
    )
