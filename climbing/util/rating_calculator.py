from datetime import datetime
from uuid import UUID, uuid4

from dateutil.relativedelta import relativedelta
from fastapi import Request
from pydantic import UUID4
from sqlalchemy import and_, case, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased, selectinload
from sqlalchemy.sql import Select
from sqlmodel import col

from climbing.core.score_maps import category_to_score_map, place_to_score_map
from climbing.crud import ascent as crud_ascent
from climbing.crud import competition_participant as crud_competition_participant
from climbing.db.models.ascent import Ascent
from climbing.db.models.competition import Competition
from climbing.db.models.competition_participant import CompetitionParticipant
from climbing.db.models.route import Route
from climbing.db.models.user import User
from climbing.schemas.ascent import AscentReadRatingWithRoute, AscentReadWithRoute
from climbing.schemas.base_read_classes import CompetitionRead, UserRead
from climbing.schemas.competition_participant import CompetitionParticipantReadRating
from climbing.schemas.filters.rating_filter import RatingFilter
from climbing.schemas.score import Score


class RatingCalculator:
    """Users rating calculator class"""

    session: AsyncSession
    categories_case = case(category_to_score_map, value=Route.category)
    _start_date: datetime
    _end_date: datetime
    routes_competition_table: dict[int, list[User]]
    user_routes_ascent_table: dict[UUID4, list[AscentReadWithRoute]]
    _filter_params: RatingFilter | None = None
    _scores: dict[UUID4, Score]
    COUNT_OF_ROUTES_TAKEN_IN_ACCOUNT = 5

    def __init__(
        self, session: AsyncSession, filter_params: RatingFilter | None = None
    ) -> None:
        self.session = session
        self.set_date_range(datetime.now())
        self._filter_params = filter_params
        self._scores = {}

    async def get_user_rating_ascents(
        self, user_id: UUID4, request: Request
    ) -> list[AscentReadRatingWithRoute]:
        """Returns list of user's ascents with flag if it is in allowed date range"""
        stmt = (
            select(
                Ascent,
                and_(
                    col(Ascent.date) >= self._start_date,
                    col(Ascent.date) <= self._end_date,
                ).label("taken_in_account"),
            )
            .join(Route)
            .where(col(Ascent.user_id) == user_id)
            .order_by(
                desc("taken_in_account"), desc(self.categories_case.label("route_cost"))
            )
            .options(selectinload(Ascent.route).selectinload("*"))
        )

        executed = await self.session.execute(stmt)
        raw_result = executed.all()
        result: list[AscentReadRatingWithRoute] = []
        taken_in_account_count = 0
        for row in raw_result:
            row.t[0].set_absolute_image_urls(request=request)
            result.append(
                AscentReadRatingWithRoute.model_validate(
                    row.t[0], update={"taken_in_account": row.t[1]}
                )
            )
            taken_in_account_count += int(result[-1].taken_in_account)
        date_sort_start_offset = min(
            taken_in_account_count, self.COUNT_OF_ROUTES_TAKEN_IN_ACCOUNT
        )
        return result[:date_sort_start_offset] + sorted(
            result[date_sort_start_offset:],
            key=lambda ascent: ascent.date,
            reverse=True,
        )

    async def calc_routes_competition(self, request: Request) -> None:
        ascents_with_score = (
            select(
                Ascent,
                self.categories_case.label("route_cost"),
                func.row_number()
                .over(
                    partition_by=col(Ascent.user_id),
                    order_by=desc(self.categories_case),
                )
                .label("route_priority"),
            )
            .options(*crud_ascent.select_options)
            .options(selectinload(Ascent.route))
            .where(col(Ascent.date) >= self._start_date)
            .where(col(Ascent.date) <= self._end_date)
            .join(Route)
            .group_by(col(Ascent.user_id), col(Ascent.route_id))
            .order_by(desc("route_priority"))
        )
        subq = ascents_with_score.subquery().alias("ascents_subq")
        aliased_subq = aliased(Ascent, subq, name="ascents_subq")
        users_with_ascents_score = (
            select(
                User,
                func.coalesce(func.sum(subq.c.route_cost), 0).label("score"),
                aliased_subq,
            )
            .outerjoin(aliased_subq, col(aliased_subq.user_id) == User.id)
            .where(
                or_(
                    subq.c.route_priority <= self.COUNT_OF_ROUTES_TAKEN_IN_ACCOUNT,
                    subq.c.route_priority is None,  # type: ignore
                )
            )
            .group_by(col(User.id))
            .order_by(desc("score"))
            .options(selectinload(aliased_subq.route).selectinload("*"))
        )

        users_with_ascents_score = self._filtered_query(users_with_ascents_score)

        self.routes_competition_table = {}
        self.user_routes_ascent_table = {}
        user: User
        ascents_score: int
        ascent: Ascent
        for user, ascents_score, ascent in (
            await self.session.execute(users_with_ascents_score)
        ).all():
            if self.user_routes_ascent_table.get(user.id, None) is None:
                self.user_routes_ascent_table[user.id] = []
            ascent.set_absolute_image_urls(request)
            self.user_routes_ascent_table[user.id].append(
                AscentReadWithRoute.model_validate(ascent)
            )
            if ascents_score not in self.routes_competition_table:
                self.routes_competition_table[ascents_score] = []
            self.routes_competition_table[ascents_score].append(user)

    def fill_routes_competition_scores(self) -> None:
        """Add competition based on ascents to scores dict"""
        place = 0
        previous_score = -1.0
        ascent_competition = self._get_ascent_competition()
        for score, users in sorted(
            self.routes_competition_table.items(),
            key=lambda x: x[0],
            reverse=True,
        ):
            if score != previous_score:
                place += 1
                previous_score = score
            rating_score = self.get_place_score(place, len(users)) if score > 0 else 0
            rating_score *= ascent_competition.ratio
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
                        user=UserRead.model_validate(user),
                        competition=ascent_competition,
                        score=rating_score,
                    )
                )

    def _fill_participants_scores(
        self,
        participants: list[CompetitionParticipant],
        place: int,
        ratio: float,
    ):
        rating_score = self.get_place_score(place, len(participants)) * ratio
        for participant in participants:
            if participant.user_id not in self._scores:
                self._scores[participant.user_id] = Score(
                    user=UserRead.model_validate(participant.user),
                    place=-1,
                )
            self._scores[participant.user_id].participations.append(
                CompetitionParticipantReadRating.model_validate(participant)
            )
            self._scores[participant.user_id].participations[-1].place = place
            self._scores[participant.user_id].participations[-1].score = rating_score
            self._scores[participant.user_id].score += rating_score

    async def fill_other_competition_scores(self) -> None:
        """Add scores from all competitions in database"""

        def competition_participants_query_modifier(query: Select) -> Select:
            query = (
                query.join(Competition)
                .join(
                    User, onclause=col(User.id) == col(CompetitionParticipant.user_id)
                )
                .where(col(Competition.date) >= self._start_date)
                .where(col(Competition.date) <= self._end_date)
                .order_by(col(Competition.date), col(CompetitionParticipant.place))
            )
            return self._filtered_query(query)

        competition_participants = await crud_competition_participant.get_all(
            session=self.session,
            query_modifier=competition_participants_query_modifier,
        )

        competition_id: UUID4 | None = None
        place_people: list[CompetitionParticipant] = []
        previous_place = 0
        real_place = 1
        for participant in competition_participants:
            if participant.competition_id != competition_id:
                if len(place_people) > 0:
                    self._fill_participants_scores(
                        place_people,
                        real_place,
                        ratio=place_people[0].competition.ratio,
                    )
                real_place = 1
                previous_place = real_place
                place_people = [participant]
                competition_id = participant.competition_id
            elif previous_place != participant.place:
                self._fill_participants_scores(
                    place_people,
                    real_place,
                    ratio=place_people[0].competition.ratio,
                )
                previous_place = participant.place
                real_place += len(place_people)
                place_people = [participant]
            else:
                place_people.append(participant)
        if len(place_people) > 0:
            self._fill_participants_scores(
                place_people,
                real_place,
                ratio=place_people[0].competition.ratio,
            )

    async def fill_ascents(self, request: Request) -> None:
        inner_query = select(
            Ascent,
            func.row_number()
            .over(
                partition_by=[col(Ascent.user_id), col(Ascent.route_id)],
                order_by=col(Ascent.date).desc(),
            )
            .label("ascent_rank"),
        )
        if self._filter_params is not None:
            inner_query = inner_query.join(
                User, onclause=col(Ascent.user_id) == col(User.id)
            )
            inner_query = self._filtered_query(inner_query)
        inner_subq = inner_query.subquery()
        query = (
            select(aliased(Ascent, inner_subq))
            .where(inner_subq.c.ascent_rank == 1)
            .options(*crud_ascent.select_options)
        )

        all_ascents = (await self.session.execute(query)).scalars().all()
        for ascent in all_ascents:
            ascent.route.set_absolute_image_urls(request)
            ascent_read = AscentReadWithRoute.model_validate(ascent)
            if ascent.user_id in self._scores:
                self._scores[ascent.user_id].ascents.append(ascent_read)
            else:
                self._scores[ascent.user_id] = Score(
                    user=UserRead.model_validate(ascent.user),
                    place=-1,
                    score=0,
                    ascents_score=0,
                    ascents=[ascent_read],
                )

    def set_date_range(
        self, end_date: datetime, start_date: datetime | None = None
    ) -> None:
        """Sets date range for rating calculation"""
        self._end_date = end_date.replace(
            hour=0, minute=0, second=0, microsecond=0
        ) + relativedelta(
            hours=23,
            minutes=59,
            seconds=59,
            microseconds=999999,
        )
        self._start_date = start_date or (
            self._end_date + relativedelta(months=-1, days=-15)
        )

    def _get_ascent_competition(self) -> CompetitionRead:
        """Get fake competition based on ascents"""

        competition_fake_id: UUID4 = UUID(hex="00000000-0000-4000-8000-000000000000")
        return CompetitionRead(
            id=competition_fake_id,
            name="5 лучших пролазов",
            date=self._end_date.date(),
            ratio=1.5,
        )

    def _filtered_query(self, query: Select) -> Select:
        if self._filter_params:
            if self._filter_params.is_student is not None:
                query = query.where(
                    col(User.is_student) == self._filter_params.is_student
                )
            if self._filter_params.sex is not None:
                query = query.where(col(User.sex) == self._filter_params.sex.value)
        return query

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
                    score.place = sorted_scores[i - 1].place + place_people_count
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
