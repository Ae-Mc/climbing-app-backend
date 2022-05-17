from fastapi import APIRouter, Request, status
from fastapi.param_functions import Depends
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from climbing.core import responses
from climbing.core.security import current_user, fastapi_users
from climbing.core.user_manager import UserManager, get_user_manager
from climbing.crud import ascent as crud_ascent
from climbing.crud.crud_route import route as crud_route
from climbing.db.models import Route, User
from climbing.db.session import get_async_session
from climbing.schemas import RouteReadWithImages, UserRead
from climbing.schemas.ascent import AscentReadWithAll

router = APIRouter()


@router.get(
    "",
    response_model=list[UserRead],
    name="users:all_users",
    dependencies=[Depends(current_user)],
    responses={**responses.LOGIN_REQUIRED},
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
    responses=responses.LOGIN_REQUIRED,
)
async def delete_me(
    async_session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
    user_manager: UserManager = Depends(get_user_manager),
):
    """Удаление текущего пользователя"""
    user_routes: list[Route] = (
        (
            await async_session.execute(
                select(Route).where(Route.author_id == user.id)
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
    response_model=list[RouteReadWithImages],
    name="users:my_routes",
    responses=responses.LOGIN_REQUIRED,
)
async def read_user_routes(
    request: Request,
    async_session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    """Список трасс текущего пользователя"""
    statement = (
        select(Route)
        .where(Route.author_id == user.id)
        .options(selectinload(Route.images))
    )
    _routes: list[Route] = (
        (await async_session.execute(statement)).scalars().all()
    )
    for _route in _routes:
        _route.set_absolute_image_urls(request)
    return _routes


@router.get(
    "/me/ascents",
    response_model=list[AscentReadWithAll],
    name="users:my_ascents",
    responses=responses.LOGIN_REQUIRED,
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


router.include_router(fastapi_users.get_users_router())
