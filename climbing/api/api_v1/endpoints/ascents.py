from datetime import datetime, timedelta

from fastapi import APIRouter, Body, Depends, Path, Request
from fastapi_users_db_sqlmodel import AsyncSession
from pydantic import UUID4
from sqlalchemy import asc, desc
from sqlalchemy.sql.selectable import Select

from climbing.core.responses import ID_NOT_FOUND, UNAUTHORIZED
from climbing.core.security import current_active_user
from climbing.crud import ascent as crud_ascent
from climbing.crud import route as crud_route
from climbing.db.models.ascent import Ascent, AscentCreate
from climbing.db.models.user import User
from climbing.db.session import get_async_session
from climbing.schemas.ascent import AscentReadWithAll
from climbing.schemas.filters.ascents_filter import AscentsFilter
from climbing.schemas.filters.order_enum import Order

router = APIRouter()


@router.get("", response_model=list[AscentReadWithAll], name="ascents:all")
async def ascents(
    request: Request,
    filter: AscentsFilter = Depends(),
    session: AsyncSession = Depends(get_async_session),
):
    """Получение списка всех подъёмов"""

    def query_modifier(query: Select[Ascent]) -> Select[Ascent]:
        if filter.date_from is not None:
            query = query.where(Ascent.date > filter.date_from)
        if filter.is_flash is not None:
            query = query.where(Ascent.is_flash == filter.is_flash)
        if filter.route_id is not None:
            query = query.where(Ascent.route_id == filter.route_id)
        if filter.user_id is not None:
            query = query.where(Ascent.user_id == filter.user_id)
        match (filter.sort_by_date):
            case Order.ASCENDING:
                query = query.order_by(asc(Ascent.date))
            case Order.DESCENDING:
                query = query.order_by(desc(Ascent.date))
            case None:
                pass
        return query

    _ascents = await crud_ascent.get_all(session, query_modifier)
    for _ascent in _ascents:
        _ascent.set_absolute_image_urls(request)
    return _ascents


@router.get(
    "/recent", response_model=list[AscentReadWithAll], name="ascents:recent"
)
async def recent_ascents(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
):
    """Получение списка недавних подъёмов"""

    return await ascents(
        request=request,
        filter=AscentsFilter(
            date_from=datetime.now() - timedelta(days=45),
            sort_by_date=Order.DESCENDING,
        ),
        session=session,
    )


@router.post(
    "",
    response_model=AscentReadWithAll,
    name="ascents:create_ascent",
    responses={**ID_NOT_FOUND.docs(), **UNAUTHORIZED.docs()},
)
async def ascent_create(
    request: Request,
    date: datetime = Body(...),
    is_flash: bool = Body(...),
    route_id: UUID4 = Body(...),
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    """Добавление подъёма"""
    route = await crud_route.get(session, row_id=route_id)
    if route is None:
        raise ID_NOT_FOUND.exception()
    _ascent = await crud_ascent.create(
        session,
        AscentCreate(
            date=date,
            is_flash=is_flash,
            route_id=route_id,
            user_id=user.id,
        ),
    )
    _ascent.set_absolute_image_urls(request)
    return _ascent


@router.get(
    "/{ascent_id}",
    response_model=AscentReadWithAll,
    name="ascents:ascent",
    responses=ID_NOT_FOUND.docs(),
)
async def ascent(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
    ascent_id: UUID4 = Path(...),
):
    """Получение подъёма по ID"""
    _ascent = await crud_ascent.get(session, ascent_id)
    if _ascent is None:
        raise ID_NOT_FOUND.exception()
    _ascent.set_absolute_image_urls(request)
    return _ascent


@router.delete(
    "/{ascent_id}",
    response_model=AscentReadWithAll,
    name="ascents:delete_ascent",
    responses={**ID_NOT_FOUND.docs(), **UNAUTHORIZED.docs()},
)
async def ascent_remove(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
    ascent_id: UUID4 = Path(...),
    user: User = Depends(current_active_user),
):
    """Удаление подъёма по ID"""
    _ascent = await crud_ascent.get(session, row_id=ascent_id)
    if _ascent is None:
        raise ID_NOT_FOUND.exception()
    if _ascent.user_id != user.id and not user.is_superuser:
        raise UNAUTHORIZED.exception()
    _ascent = await crud_ascent.remove(session, row_id=ascent_id)
    _ascent.set_absolute_image_urls(request)
    return _ascent
