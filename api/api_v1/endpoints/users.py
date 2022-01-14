from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from api.deps import get_database
from crud import user
import schemas


router = APIRouter()

schema = OAuth2PasswordBearer(tokenUrl="users")


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


@router.get("/", response_model=List[schemas.User])
def read_users(
    database: Session = Depends(get_database),
):
    """Список пользователей"""
    return user.get_all(database)


@router.post("/", response_model=schemas.User)
def add_user(
    database: Session = Depends(get_database),
    new_user: schemas.UserCreate = Depends(),
):
    """Создание нового пользователя. Должно быть доступно только
    админимтратору"""
    if user.get_by_username(database, new_user.username) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с таким никнеймом уже существует",
        )
    return user.create(database=database, entity=new_user)
