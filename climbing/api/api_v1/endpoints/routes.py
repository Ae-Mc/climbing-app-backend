from datetime import date

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi_users_db_sqlalchemy import AsyncSession
from pydantic import ValidationError
from sqlalchemy import select

from climbing import models, schemas
from climbing.api.deps import FileStorage
from climbing.core import responses
from climbing.core.security import current_active_user
from climbing.db.session import get_async_session

router = APIRouter()


@router.get("", response_model=list[schemas.Route], name="routes:all")
async def routes(session: AsyncSession = Depends(get_async_session)):
    statement = select(models.Route)
    return (await session.execute(statement)).scalars().all()


@router.post(
    "",
    response_model=list[schemas.Route],
    name="routes:new",
    responses=responses.LOGIN_REQUIRED,
)
async def create_route(
    name: str = Form(..., min_length=1, max_length=150),
    category: schemas.Category = Form(...),
    mark_color: str = Form(..., min_length=4, max_length=100),
    author: str = Form(None, max_length=150),
    description: str = Form(...),
    creation_date: date = Form(...),
    images: list[UploadFile] = File([], media_type="image/*"),
    user: models.User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
    file_storage: FileStorage = Depends(),
):
    try:
        route = schemas.RouteCreate(
            name=name,
            category=category,
            mark_color=mark_color,
            author=author,
            description=description,
            creation_date=creation_date,
            images=images,
        )
    except ValidationError as err:
        raise RequestValidationError(err.raw_errors) from err
    return None
