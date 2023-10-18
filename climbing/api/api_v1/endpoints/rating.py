from datetime import datetime
from typing import List

from dateutil.relativedelta import relativedelta
from fastapi import APIRouter, Depends, Query, Request
from fastapi_users_db_sqlmodel import UUID4, AsyncSession, selectinload
from pydantic import BaseModel, Field
from sqlalchemy import case, desc, func, or_, select

from climbing.core.score_maps import category_to_score_map, place_to_score_map
from climbing.crud import ascent as crud_ascent
from climbing.db.models.ascent import Ascent
from climbing.db.models.category import Category
from climbing.db.models.competition import Competition
from climbing.db.models.competition_participant import CompetitionParticipant
from climbing.db.models.route import Route
from climbing.db.models.user import User
from climbing.db.session import get_async_session
from climbing.schemas.ascent import AscentReadWithRoute
from climbing.schemas.competition_participant import (
    CompetitionParticipantReadWithAll,
)
from climbing.schemas.score import Score

router = APIRouter()


def get_place_score(place: int, users_count: int) -> float:
    """Calculates score for place"""

    return sum(
        [
            place_to_score_map.get(place, 0)
            for place in range(place, users_count + place)
        ]
    ) / (users_count)


@router.get(
    "",
    name="rating:rating",
    response_model=List[Score],
)
async def rating(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
    start_date: datetime = Query(None),
    end_date: datetime = Query(None),
) -> List[Score]:
    """Получение подъёмов за последнии полтора месяца для рейтинга"""

    if end_date is None:
        end_date = datetime.now()
    end_date = end_date.date() + relativedelta(
        hours=23, minutes=59, seconds=59
    )

    if start_date is None:
        start_date = end_date + relativedelta(months=-1, days=-15)
    start_date = start_date.date()

    categories_case = case(value=Route.category, whens=category_to_score_map)
    # Calculate routes scores
    ascents_with_score = (
        select(
            Ascent,
            categories_case.label("route_cost"),
            func.row_number()
            .over(partition_by=Ascent.user_id, order_by=desc(categories_case))
            .label("route_priority"),
        )
        .options(*crud_ascent.select_options)
        .where(Ascent.date >= start_date)
        .where(Ascent.date <= end_date)
        .join(Route)
        .group_by(Ascent.user_id, Ascent.route_id)
        .order_by(desc("route_priority"))
    )
    subq = ascents_with_score.subquery()
    users_with_ascents_score = (
        select(
            User, func.coalesce(func.sum(subq.c.route_cost), 0).label("score")
        )
        .outerjoin_from(User, subq, subq.c.user_id == User.id)
        .where(
            or_(
                subq.c.route_priority < 6,
                # pylint: disable=singleton-comparison
                subq.c.route_priority == None,  # noqa: E711
            )
        )
        .group_by(User.id)
        .order_by(desc("score"))
    )

    user: User
    routes_competition_table: dict[float, list[User]] = {}
    for user, ascents_score in (
        await session.execute(users_with_ascents_score)
    ).all():
        if ascents_score not in routes_competition_table:
            routes_competition_table[ascents_score] = []
        routes_competition_table[ascents_score].append(user)

    scores: dict[UUID4, Score] = {}
    place = 0
    previous_score = -1.0
    for score, users in sorted(
        routes_competition_table.items(), key=lambda x: x[0], reverse=True
    ):
        if score != previous_score:
            place += 1
            previous_score = score
        rating_score = get_place_score(place, len(users) or 1)
        for user in users:
            scores[user.id] = Score(
                user=user,
                score=rating_score,
                ascents_score=score,
                place=place,
            )

    # Fill ascents property
    all_ascents = await crud_ascent.get_all(
        session=session,
        # pylint: disable=no-member
        query_modifier=lambda query: query.order_by(Ascent.date.desc()),
    )
    for ascent in all_ascents:
        ascent.route.set_absolute_image_urls(request)
        scores[ascent.user_id].ascents.append(
            AscentReadWithRoute.from_orm(ascent)
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

    for participant in competition_participants:
        current_score = scores[participant.user_id]
        current_score.participations.append(
            CompetitionParticipantReadWithAll.from_orm(participant)
        )
        participants_on_same_place = [
            _participant
            for _participant in participant.competition.participants
            if _participant.place == participant.place
        ]
        current_score.score += (
            get_place_score(participant.place, len(participants_on_same_place))
            * participant.competition.ratio
        )
    sorted_scores = sorted(
        scores.values(), key=lambda score: score.score, reverse=True
    )
    if sorted_scores:
        sorted_scores[0].place = 1
        place_people_count = 0
        for i, score in tuple(enumerate(sorted_scores))[1:]:
            score.place = sorted_scores[i - 1].place
            place_people_count += 1
            if sorted_scores[i - 1].score != score.score:
                score.place += place_people_count
                place_people_count = 0
    return sorted_scores


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
