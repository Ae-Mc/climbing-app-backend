from datetime import datetime
from typing import Sequence

from dateutil.relativedelta import relativedelta
from fastapi import APIRouter, HTTPException, Path, Request, status
from fastapi.param_functions import Depends
from fastapi_users.exceptions import UserNotExists
from pydantic import UUID4
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import Select
from sqlmodel import col

from climbing.core import responses
from climbing.core.security import current_superuser, current_user, fastapi_users
from climbing.core.user_manager import UserManager, get_user_manager
from climbing.crud import ascent as crud_ascent
from climbing.crud import competition as crud_competition
from climbing.crud import competition_participant as crud_competition_participant
from climbing.crud import route as crud_route
from climbing.db.models import Route, User
from climbing.db.models.ascent import Ascent, AscentUpdate
from climbing.db.models.competition import Competition, CompetitionUpdate
from climbing.db.models.competition_participant import (
    CompetitionParticipant,
    CompetitionParticipantUpdate,
)
from climbing.db.models.route import RouteUpdate
from climbing.db.models.user import UserUpdate
from climbing.db.session import get_async_session
from climbing.schemas import UserRead
from climbing.schemas.ascent import AscentReadWithAll
from climbing.schemas.competition import CompetitionReadWithAll
from climbing.schemas.expiring_ascent import ExpiringAscent
from climbing.schemas.route import RouteReadWithAll

router = APIRouter()


@router.get(
    "",
    response_model=list[UserRead],
    name="users:all_users",
    dependencies=[Depends(current_user)],
    responses=responses.UNAUTHORIZED.docs(),
)
async def read_users(
    async_session: AsyncSession = Depends(get_async_session),
):
    """Список пользователей"""
    return (await async_session.execute(select(User))).scalars().all()


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    name="users:delete_me",
    responses=responses.UNAUTHORIZED.docs(),
)
async def delete_me(
    async_session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
    user_manager: UserManager = Depends(get_user_manager),
):
    """Удаление текущего пользователя"""
    user_routes: Sequence[Route] = (
        (
            await async_session.execute(
                select(Route).where(col(Route.author_id) == user.id)
            )
        )
        .scalars()
        .all()
    )
    for route in user_routes:
        await crud_route.remove(async_session, row_id=route.id)
    await user_manager.delete(user)


@router.get(
    "/me/routes",
    response_model=list[RouteReadWithAll],
    name="users:my_routes",
    responses=responses.UNAUTHORIZED.docs(),
)
async def read_user_routes(
    request: Request,
    async_session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    """Список трасс текущего пользователя"""
    _routes = await crud_route.get_for_user(async_session, user.id)
    for _route in _routes:
        _route.set_absolute_image_urls(request)
    return _routes


@router.get(
    "/me/ascents",
    response_model=list[AscentReadWithAll],
    name="users:my_ascents",
    responses=responses.UNAUTHORIZED.docs(),
)
async def read_user_ascents(
    request: Request,
    async_session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    """Список подъёмов текущего пользователя"""
    ascents = await crud_ascent.get_for_user(async_session, user.id)
    for ascent in ascents:
        ascent.set_absolute_image_urls(request)
    return ascents


@router.get(
    "/me/competitions",
    name="users:my_competitions",
    response_model=list[CompetitionReadWithAll],
    responses=responses.UNAUTHORIZED.docs(),
)
async def read_user_competitions(
    async_session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    """Список организованных текущим пользователем соревнований"""
    competitions = await crud_competition.get_for_organizer(async_session, user.id)
    return competitions


@router.get(
    "/me/ascents/expiring",
    response_model=list[ExpiringAscent],
    name="users:my_ascents",
    responses=responses.UNAUTHORIZED.docs(),
)
async def read_user_expiring_ascents(
    request: Request,
    async_session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    """Список подъёмов текущего пользователя, которые скоро исчезнут из
    рейтинга"""
    end_date = datetime.now()
    end_date = end_date.replace(
        hour=0, minute=0, second=0, microsecond=0
    ) + relativedelta(days=2)
    start_date = end_date + relativedelta(months=-1, days=-15)

    ascents = await crud_ascent.get_for_user(
        async_session, user.id, start_date, end_date
    )
    for ascent in ascents:
        ascent.set_absolute_image_urls(request)
    return sorted(
        list(
            map(
                lambda ascent: ExpiringAscent(
                    time_to_expire=ascent.date - start_date,
                    ascent=ascent,
                ),
                ascents,
            )
        ),
        key=lambda x: x.time_to_expire,
    )


@router.put(
    "/replace/{user_id}/{replacement_id}",
    dependencies=(Depends(current_superuser),),
    responses={
        **responses.ID_NOT_FOUND.docs(),
        **responses.UNAUTHORIZED.docs(),
        **responses.SUPERUSER_REQUIRED.docs(),
    },
    status_code=204,
)
async def replace_with_new_user(
    user_id: UUID4 = Path(...),
    replacement_id: UUID4 = Path(...),
    session: AsyncSession = Depends(get_async_session),
    user_manager: UserManager = Depends(get_user_manager),
):
    def participation_query_modifier(query: Select) -> Select:
        return query.where(col(CompetitionParticipant.user_id) == user_id)

    def ascent_query_modifier(query: Select) -> Select:
        return query.where(col(Ascent.user_id) == user_id)

    def route_query_modifier(query: Select) -> Select:
        return query.where(col(Route.author_id) == user_id)

    def competition_query_modifier(query: Select) -> Select:
        return query.where(col(Competition.organizer_id) == user_id)

    try:
        user = await user_manager.get(user_id)
    except UserNotExists:
        raise HTTPException(
            status_code=404, detail=f'User with id "{user_id}" not found'
        )
    try:
        replacement = await user_manager.get(replacement_id)
    except UserNotExists:
        raise HTTPException(
            status_code=404, detail=f'User with id "{replacement_id}" not found'
        )
    participations = await crud_competition_participant.get_all(
        session=session, query_modifier=participation_query_modifier
    )
    for participation in participations:
        new_participation = CompetitionParticipantUpdate.model_validate(participation)
        new_participation.user_id = replacement.id
        await crud_competition_participant.update(
            session=session,
            db_entity=participation,
            new_entity=new_participation,
        )
    ascents = await crud_ascent.get_all(
        session=session, query_modifier=ascent_query_modifier
    )
    for ascent in ascents:
        new_ascent = AscentUpdate.model_validate(ascent)
        new_ascent.user_id = replacement.id
        await crud_ascent.update(
            session=session, db_entity=ascent, new_entity=new_ascent
        )
    routes = await crud_route.get_all(
        session=session, query_modifier=route_query_modifier
    )
    for route in routes:
        new_route = RouteUpdate.model_validate(route)
        new_route.author_id = replacement.id
        await crud_route.update(session=session, db_entity=route, new_entity=new_route)
    competitions = await crud_competition.get_all(
        session=session, query_modifier=competition_query_modifier
    )
    for competition in competitions:
        new_competition = CompetitionUpdate.model_validate(competition)
        new_competition.organizer_id = replacement.id
        await crud_competition.update(
            session=session, db_entity=competition, new_entity=new_competition
        )

    await user_manager.delete(user)


router.include_router(fastapi_users.get_users_router(UserRead, UserUpdate))  # type: ignore
