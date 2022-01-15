from typing import List

from fastapi import APIRouter
from fastapi.param_functions import Depends
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.future import select

from climbing.api.deps import get_database
from climbing.core.security import fastapi_users
from climbing.models.user import User
from climbing.schemas.user import User as PydanticUser

router = APIRouter()


@router.get(
    "",
    response_model=List[PydanticUser],
    name="users:all_users",
)
async def read_users(
    database: AsyncSession = Depends(get_database),
):
    """Список пользователей"""
    statement = select(User)
    result: Result = await database.execute(statement)
    return result.all()


router.include_router(fastapi_users.get_users_router())
