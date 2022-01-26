from fastapi import APIRouter, status
from fastapi.param_functions import Depends
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from climbing.core import responses
from climbing.core.security import (
    current_superuser,
    current_user,
    fastapi_users,
)
from climbing.core.user_manager import UserManager, get_user_manager
from climbing.crud.crud_route import route as crud_route
from climbing.db.models import Route, User
from climbing.db.session import get_async_session
from climbing.schemas import RouteReadWithImages, UserRead

router = APIRouter()


@router.get(
    "",
    response_model=list[UserRead],
    name="users:all_users",
    dependencies=[Depends(current_superuser)],
    responses={**responses.SUPERUSER_REQUIRED, **responses.LOGIN_REQUIRED},
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
                select(Route).where(Route.uploader_id == user.id)
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
    async_session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    """Список трасс текущего пользователя"""
    statement = (
        select(Route)
        .where(Route.uploader_id == user.id)
        .options(selectinload(Route.images))
    )
    return (await async_session.execute(statement)).scalars().all()


router.include_router(fastapi_users.get_users_router())
