from datetime import datetime

from dateutil.relativedelta import relativedelta
from fastapi import APIRouter, Depends, Query, Request
from fastapi_users_db_sqlmodel import AsyncSession, selectinload
from pydantic import BaseModel, Field
from sqlalchemy import case, desc, func, select

from climbing.core.score_maps import category_to_score_map, place_to_score_map
from climbing.crud import ascent as crud_ascent
from climbing.db.models.ascent import Ascent
from climbing.db.models.category import Category
from climbing.db.models.competition import Competition
from climbing.db.models.competition_participant import CompetitionParticipant
from climbing.db.models.route import Route
from climbing.db.models.user import User
from climbing.db.session import get_async_session
from climbing.schemas.competition_participant import (
    CompetitionParticipantReadWithAll,
)
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

    # Calculate routes scores
    ascents_with_score = (
        select(
            Ascent,
            case(value=Route.category, whens=category_to_score_map).label(
                "route_cost"
            ),
            func.row_number()
            .over(
                partition_by=Ascent.user_id,
                order_by=desc(
                    case(value=Route.category, whens=category_to_score_map)
                ),
            )
            .label("route_priority"),
        )
        .options(*crud_ascent.select_options)
        .where(Ascent.date >= start_date)
        .where(Ascent.date <= end_date)
        .join(Route)
        .group_by(Ascent.user_id, Ascent.route_id)
        .order_by(
            desc(
                case(
                    value=Route.category,
                    whens=category_to_score_map,
                )
            )
        )
    )
    # pprint((await session.execute(stmt)).first())
    _ascents: list[Ascent] = (
        (await session.execute(ascents_with_score)).scalars().all()
    )
    for ascent in _ascents:
        ascent.set_absolute_image_urls(request)
    outer_statement = (
        select(Ascent, func.sum(ascents_with_score.c.route_cost))
        .options(*crud_ascent.select_options)
        .join(Ascent, ascents_with_score.c.id == Ascent.id)
        .where(ascents_with_score.c.route_priority < 6)
        .group_by(Ascent.user_id)
    )
    ascent: Ascent
    score: float
    scores = {
        ascent.user_id: Score(
            user=ascent.user,
            score=score,
            ascents=[x for x in _ascents if x.user_id == ascent.user_id],
            participations=[],
        )
        for ascent, score in (await session.execute(outer_statement)).all()
    }

    users: list[User] = (
        (await session.execute(select(User).options())).scalars().all()
    )

    for user in users:
        if user.id not in scores:
            scores[user.id] = Score(
                user=user, score=0, ascents=[], participations=[]
            )

    # Calculate competitions scores
    competition_participants: list[CompetitionParticipant] = (
        (
            await session.execute(
                select(CompetitionParticipant)
                .options(
                    selectinload(
                        CompetitionParticipant.competition
                    ).selectinload(Competition.participants),
                    selectinload(CompetitionParticipant.user),
                )
                .join(Competition)
                .where(Competition.date >= start_date)
                .where(Competition.date <= end_date)
            )
        )
        .scalars()
        .all()
    )

    score: Score
    for user_id, score in scores.items():
        participations = [
            x for x in competition_participants if x.user_id == user_id
        ]
        for participation in participations:
            score.participations.append(
                CompetitionParticipantReadWithAll.from_orm(participation)
            )
            number_of_participants_on_same_place = len(
                [
                    0
                    for participant in participation.competition.participants
                    if participant.place == participation.place
                ]
            )
            competition_score = (
                sum(
                    [
                        place_to_score_map.get(place, 0)
                        for place in range(
                            participation.place,
                            number_of_participants_on_same_place
                            + participation.place,
                        )
                    ]
                )
                / number_of_participants_on_same_place
                * participation.competition.ratio
            )

            score.score += competition_score
    return sorted(scores.values(), key=lambda score: score.score, reverse=True)


class CategoryToScore(BaseModel):
    """Модель для описания цены категории"""

    category: Category = Field(..., title="Категория")
    score: float = Field(..., title="Количество очков за прохождение")


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
