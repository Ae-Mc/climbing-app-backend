from datetime import date, datetime
from uuid import uuid4

from dateutil.relativedelta import relativedelta
from fastapi import Request
from pydantic import UUID4
from sqlalchemy import case, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import Select

from climbing.core.score_maps import category_to_score_map, place_to_score_map
from climbing.crud import ascent as crud_ascent
from climbing.crud import (
    competition_participant as crud_competition_participant,
)
from climbing.db.models.ascent import Ascent
from climbing.db.models.competition import Competition
from climbing.db.models.competition_participant import CompetitionParticipant
from climbing.db.models.route import Route
from climbing.db.models.user import User
from climbing.schemas.ascent import AscentReadWithRoute
from climbing.schemas.base_read_classes import CompetitionRead, UserRead
from climbing.schemas.competition_participant import (
    CompetitionParticipantReadRating,
)
from climbing.schemas.rating_filter import RatingFilter
from climbing.schemas.score import Score


class RatingCalculator:
    """Users rating calculator class"""

    session: AsyncSession
    categories_case = case(value=Route.category, whens=category_to_score_map)
    _start_date: datetime
    _end_date: datetime
    routes_competition_table: dict[float, list[User]]
    filter: RatingFilter | None = None
    _scores: dict[UUID4, Score]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.set_date_range(datetime.now())
        self._scores = {}

    async def calc_routes_competition(self) -> None:
        ascents_with_score = (
            select(
                Ascent,
                self.categories_case.label("route_cost"),
                func.row_number()
                .over(
                    partition_by=Ascent.user_id,
                    order_by=desc(self.categories_case),
                )
                .label("route_priority"),
            )
            .options(*crud_ascent.select_options)
            .where(Ascent.date >= self._start_date)
            .where(Ascent.date <= self._end_date)
            .join(Route)
            .group_by(Ascent.user_id, Ascent.route_id)
            .order_by(desc("route_priority"))
        )
        subq = ascents_with_score.subquery()
        users_with_ascents_score = (
            select(
                User,
                func.coalesce(func.sum(subq.c.route_cost), 0).label("score"),
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

        if self.filter:
            if self.filter.is_student is not None:
                users_with_ascents_score = users_with_ascents_score.where(
                    User.is_student == self.filter.is_student
                )

        self.routes_competition_table: dict[float, list[User]] = {}
        user: User
        ascents_score: int
        for user, ascents_score in (
            await self.session.execute(users_with_ascents_score)
        ).all():
            if ascents_score not in self.routes_competition_table:
                self.routes_competition_table[ascents_score] = []
            self.routes_competition_table[ascents_score].append(user)

    def fill_routes_competition_scores(self) -> None:
        """Add competition based on ascents to scores dict"""
        place = 0
        previous_score = -1.0
        for score, users in sorted(
            self.routes_competition_table.items(),
            key=lambda x: x[0],
            reverse=True,
        ):
            if score != previous_score:
                place += 1
                previous_score = score
            rating_score = (
                self.get_place_score(place, len(users)) if score > 0 else 0
            )
            for user in users:
                if user.id in self._scores:
                    self._scores[user.id].ascents_score = score
                    self._scores[user.id].score += rating_score
                else:
                    self._scores[user.id] = Score(
                        user=user,
                        score=rating_score,
                        ascents_score=score,
                        place=-1,
                    )
                self._scores[user.id].participations.append(
                    CompetitionParticipantReadRating(
                        id=uuid4(),
                        place=place,
                        user=UserRead.from_orm(user),
                        competition=self.get_ascent_competition(),
                        score=rating_score,
                    )
                )

    async def fill_other_competition_scores(self) -> None:
        """Add scores from all competitions in database"""

        def competition_participants_query_modifier(query: Select) -> Select:
            query = (
                query.join(Competition)
                .options(
                    selectinload(
                        CompetitionParticipant.competition
                    ).selectinload(Competition.participants),
                )
                .where(Competition.date >= self._start_date)
                .where(Competition.date <= self._end_date)
            )
            if self.filter is not None:
                if self.filter.is_student is not None:
                    query = query.join(
                        User, onclause=User.id == CompetitionParticipant.user_id
                    ).where(User.is_student == self.filter.is_student)
            return query

        competition_participants: list[
            CompetitionParticipant
        ] = await crud_competition_participant.get_all(
            session=self.session,
            query_modifier=competition_participants_query_modifier,
        )

        for participant in competition_participants:
            if participant.user_id not in self._scores:
                self._scores[participant.user_id] = Score(
                    user=UserRead.from_orm(participant.user),
                    place=-1,
                )
            current_score = self._scores[participant.user_id]
            current_score.participations.append(
                CompetitionParticipantReadRating.from_orm(participant)
            )
            participants_on_same_place = [
                _participant
                for _participant in participant.competition.participants
                if _participant.place == participant.place
            ]
            rating_score = (
                self.get_place_score(
                    participant.place, len(participants_on_same_place)
                )
                * participant.competition.ratio
            )
            current_score.participations[-1].score = rating_score
            current_score.score += rating_score

    async def fill_ascents(self, request: Request) -> None:
        def query_modifier(query: Select) -> Select:
            if self.filter is not None:
                if self.filter.is_student is not None:
                    query = query.join(
                        User, onclause=Ascent.user_id == User.id
                    ).where(User.is_student == self.filter.is_student)
            return query.order_by(Ascent.date.desc())

        all_ascents: list[Ascent] = await crud_ascent.get_all(
            session=self.session,
            query_modifier=query_modifier,
        )
        for ascent in all_ascents:
            ascent.route.set_absolute_image_urls(request)
            if ascent.user_id in self._scores:
                self._scores[ascent.user_id].ascents.append(
                    AscentReadWithRoute.from_orm(ascent)
                )
            else:
                self._scores[ascent.user_id] = Score(
                    user=UserRead.from_orm(ascent.user),
                    place=-1,
                    score=0,
                    ascents_score=0,
                    ascents=[AscentReadWithRoute.from_orm(ascent)],
                )

    def set_date_range(
        self, end_date: datetime, start_date: datetime | None = None
    ) -> None:
        """Sets date range for rating calculation"""
        self._end_date = end_date.date() + relativedelta(
            hours=23,
            minutes=59,
            seconds=59,
            microseconds=999999,
        )
        self._start_date = start_date or (
            self._end_date + relativedelta(months=-1, days=-15)
        )

    def get_ascent_competition(self) -> CompetitionRead:
        """Get fake competition based on ascents"""

        competition_fake_id: UUID4 = "00000000-0000-4000-8000-000000000000"
        return CompetitionRead(
            id=competition_fake_id,
            name="5 лучших пролазов",
            date=self._end_date.date(),
            ratio=1.0,
        )

    @property
    def scores(self) -> list[Score]:
        sorted_scores = sorted(
            self._scores.values(), key=lambda score: score.score, reverse=True
        )
        if len(sorted_scores) > 0:
            sorted_scores[0].place = 1
            place_people_count = 1
            for i, score in tuple(enumerate(sorted_scores))[1:]:
                if sorted_scores[i - 1].score != score.score:
                    score.place = (
                        sorted_scores[i - 1].place + place_people_count
                    )
                    place_people_count = 1
                else:
                    score.place = sorted_scores[i - 1].place
                    place_people_count += 1
        return sorted_scores

    @property
    def end_date(self) -> datetime:
        return self._end_date

    @property
    def start_date(self) -> datetime:
        return self._start_date

    @staticmethod
    def get_place_score(place: int, users_count: int) -> float:
        """Calculates score for place"""

        return sum(
            place_to_score_map.get(place, 0)
            for place in range(place, users_count + place)
        ) / (users_count)
