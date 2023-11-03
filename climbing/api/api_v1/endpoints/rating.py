import urllib.parse
from datetime import datetime
from io import BytesIO
from typing import List

from fastapi import APIRouter, Depends, Query, Request, Response
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from xlsxwriter import Workbook
from xlsxwriter.format import Format

from climbing.core.score_maps import category_to_score_map, place_to_score_map
from climbing.crud.crud_competition import competition as crud_competition
from climbing.db.models.competition import Competition
from climbing.db.session import get_async_session
from climbing.schemas.base_read_classes import CompetitionRead
from climbing.schemas.category_to_score import CategoryToScore
from climbing.schemas.rating_filter import RatingFilter
from climbing.schemas.score import Score
from climbing.util.rating_calculator import RatingCalculator

router = APIRouter()


async def prepare_rating(
    request: Request,
    session: AsyncSession,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    is_student: bool | None = None,
) -> RatingCalculator:
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
    return calc


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
):
    """Получение данных по рейтингу. По умолчанию временной интервал — полтора
    месяца с текущей даты"""

    return (
        await prepare_rating(
            request=request,
            session=session,
            start_date=start_date,
            end_date=end_date,
            is_student=is_student,
        )
    ).scores


@router.get(
    "/table",
    name="rating:rating_table",
    response_model=List[Score],
)
async def rating_csv(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
    start_date: datetime | None = Query(None),
    end_date: datetime | None = Query(None),
    is_student: bool | None = Query(None),
):
    """Получение данных по рейтингу. По умолчанию временной интервал — полтора
    месяца с текущей даты"""
    calc = await prepare_rating(
        request=request,
        session=session,
        start_date=start_date,
        end_date=end_date,
        is_student=is_student,
    )
    scores = calc.scores
    dataIO = BytesIO()
    workbook = Workbook(dataIO)
    worksheet = workbook.add_worksheet()
    worksheet.write(1, 0, "Место")
    worksheet.write(1, 1, "Имя участника")
    competitions: list[CompetitionRead] = list(
        map(
            CompetitionRead.from_orm,
            await crud_competition.get_all(
                session=session,
                query_modifier=lambda query: query.where(
                    Competition.date >= calc.start_date
                ).where(Competition.date <= calc.end_date),
            ),
        )
    )
    competitions.insert(0, calc.get_ascent_competition())
    format = workbook.add_format()
    format.set_align("center")
    rating_name = {True: "Студенческий", False: "НеСтуденческий", None: "Общий"}
    rating_fullname = (
        f"{rating_name[is_student]} рейтинг на {calc.end_date.date()}"
    )
    worksheet.merge_range(
        0,
        0,
        0,
        2 + len(competitions),
        data=rating_fullname,
        cell_format=format,
    )
    worksheet.write(1, 2 + len(competitions), "Итого баллы")

    for i, competition in enumerate(competitions):
        worksheet.write(
            1, 2 + i, f"{competition.name} (коэфф {competition.ratio})"
        )
    for i, score in enumerate(scores):
        participations = {
            participation.competition.id: participation
            for participation in score.participations
        }
        worksheet.write(2 + i, 0, score.place)
        worksheet.write(
            2 + i, 1, f"{score.user.last_name} {score.user.first_name}"
        )
        for j, competition in enumerate(competitions):
            if competition.id in participations:
                score_value = participations[competition.id].score
            else:
                score_value = 0
            worksheet.write(2 + i, 2 + j, score_value)
        worksheet.write(2 + i, 2 + len(competitions), score.score)
    worksheet.autofit()
    workbook.close()
    result = dataIO.getvalue()
    return Response(
        content=result,
        media_type="application/vnd.ms-excel",
        headers={
            "Content-Disposition": (
                "attachment; filename*=UTF-8''"
                + urllib.parse.quote(f"{rating_fullname}.xlsx".encode())
            )
        },
    )


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
