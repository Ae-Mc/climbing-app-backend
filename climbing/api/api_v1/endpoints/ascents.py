from datetime import datetime

from fastapi import APIRouter, Body, Depends, Path, Request
from fastapi_users_db_sqlmodel import AsyncSession
from pydantic import UUID4

from climbing.core.responses import ID_NOT_FOUND, UNAUTHORIZED
from climbing.core.security import current_active_user
from climbing.crud import ascent as crud_ascent
from climbing.crud import route as crud_route
from climbing.db.models.ascent import AscentCreate
from climbing.db.models.user import User
from climbing.db.session import get_async_session
from climbing.schemas.ascent import AscentReadWithAll

router = APIRouter()


@router.get("", response_model=list[AscentReadWithAll], name="ascents:all")
async def ascents(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
):
    """Получение списка всех подъёмов"""
    _ascents = await crud_ascent.get_all(session)
    for _ascent in _ascents:
        _ascent.set_absolute_image_urls(request)
    return _ascents


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
    if _ascent.user_id != user.id and not user.is_superuser:
        raise UNAUTHORIZED.exception()
    _ascent = await crud_ascent.remove(session, row_id=ascent_id)
    if _ascent is None:
        raise ID_NOT_FOUND.exception()
    _ascent.set_absolute_image_urls(request)
    return _ascent
