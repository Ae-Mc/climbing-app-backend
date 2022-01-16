from fastapi import APIRouter
from fastapi.param_functions import Depends
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from climbing.core import responses
from climbing.core.security import current_superuser, fastapi_users
from climbing.db.session import get_async_session
from climbing.models.user import User
from climbing.schemas.user import User as PydanticUser

router = APIRouter()


@router.get(
    "",
    response_model=list[PydanticUser],
    name="users:all_users",
    dependencies=[Depends(current_superuser)],
    responses={**responses.SUPERUSER_REQUIRED, **responses.LOGIN_REQUIRED},
)
async def read_users(
    async_session: AsyncSession = Depends(get_async_session),
):
    """Список пользователей"""
    statement = select(User).options(selectinload(User.oauth_accounts))
    return (await async_session.execute(statement)).scalars().all()


router.include_router(fastapi_users.get_users_router())
