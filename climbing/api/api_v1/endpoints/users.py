from typing import List
from fastapi.param_functions import Depends
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.future import select

from climbing.api.deps import get_database
from climbing.core.security import fastapi_users
from climbing.models.user import User
from climbing.schemas.user import User as PydanticUser

router = fastapi_users.get_users_router()


# @router.post("/", response_model=schemas.User)
# def login(
#     database: Session = Depends(get_database),
#     credentials: OAuth2PasswordRequestForm = Depends(),
# ):
#     """Вход"""
#     db_user = user.authorize(
#         database=database,
#         username=credentials.username,
#         password=credentials.password,
#     )
#     if db_user is None:
#         raise HTTPException(
#             detail="Неверный логин или пароль",
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     return db_user


@router.get("/", response_model=List[PydanticUser])
async def read_users(
    database: AsyncSession = Depends(get_database),
):
    """Список пользователей"""
    statement = select(User)
    result: Result = await database.execute(statement)
    return result.all()


# @router.post("/", response_model=schemas.User)
# def add_user(
#     database: Session = Depends(get_database),
#     new_user: schemas.UserCreate = Depends(),
# ):
#     """Создание нового пользователя. Должно быть доступно только
#     админимтратору"""
#     if user.get_by_username(database, new_user.username) is not None:
#         raise HTTPException(
#             status_code=status.HTTP_409_CONFLICT,
#             detail="Пользователь с таким никнеймом уже существует",
#         )
#     return user.create(database=database, entity=new_user)
