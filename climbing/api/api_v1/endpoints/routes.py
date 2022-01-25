from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, Path, UploadFile
from fastapi.exceptions import HTTPException, RequestValidationError
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from climbing.core import responses
from climbing.core.security import current_active_user
from climbing.crud import route as crud_route
from climbing.db.models import Category, RouteCreate, RouteRead, User
from climbing.db.session import get_async_session

router = APIRouter()


@router.get("", response_model=list[RouteRead], name="routes:all")
async def routes(session: AsyncSession = Depends(get_async_session)):
    "Получение списка всех трасс"
    return await crud_route.get_all(session)


@router.get("/{route_id}", response_model=RouteRead, name="routes:route")
async def route(
    route_id: UUID = Path(...),
    session: AsyncSession = Depends(get_async_session),
):
    "Получение трассы"
    route_instance = await crud_route.get(session, route_id)
    if route_instance:
        print(route_instance.uploader)
    return route_instance


@router.delete(
    "/{route_id}",
    name="routes:delete_route",
    responses=responses.LOGIN_REQUIRED,
)
async def delete_route(
    route_id: UUID = Path(...),
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    "Удаление трассы"
    route_instance = await crud_route.get(session, route_id)
    if route_instance:
        if route_instance.uploader_id == user.id or user.is_superuser:
            return await crud_route.remove(session, row_id=route_id)
        raise HTTPException(
            403, detail="Вы не создатель этой трассы и не администратор"
        )
    raise HTTPException(404)


@router.post(
    "",
    response_model=RouteRead,
    status_code=201,
    name="routes:new",
    responses=responses.LOGIN_REQUIRED,
)
async def create_route(
    name: str = Form(..., min_length=1, max_length=150),
    category: Category = Form(...),
    mark_color: str = Form(..., min_length=4, max_length=100),
    author: str = Form(None, max_length=150),
    description: str = Form(...),
    creation_date: date = Form(...),
    images: list[UploadFile] = File([], media_type="image/*"),
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    "Создание трассы"
    try:
        route_instance = RouteCreate(
            name=name,
            category=category,
            mark_color=mark_color,
            author=author,
            description=description,
            creation_date=creation_date,
            images=images,
            uploader=user,
        )
        created_route = await crud_route.create(session, route_instance)
        return created_route
    except ValidationError as err:
        raise RequestValidationError(err.raw_errors) from err
