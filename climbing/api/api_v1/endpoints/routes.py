from datetime import date
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    Path,
    Request,
    Response,
    UploadFile,
)
from fastapi.exceptions import HTTPException, RequestValidationError
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from climbing.core import responses
from climbing.core.security import current_active_user
from climbing.crud import route as crud_route
from climbing.db.models import Category, RouteCreate, User
from climbing.db.session import get_async_session
from climbing.schemas import RouteReadWithAll

router = APIRouter()


@router.get("", response_model=list[RouteReadWithAll], name="routes:all")
async def routes(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
):
    "Получение списка всех трасс"
    _routes = await crud_route.get_all(session)
    for _route in _routes:
        _route.set_absolute_image_urls(request)
    return _routes


@router.get(
    "/{route_id}",
    response_model=RouteReadWithAll,
    name="routes:route",
    responses=responses.ID_NOT_FOUND,
)
async def route(
    request: Request,
    route_id: UUID = Path(...),
    session: AsyncSession = Depends(get_async_session),
):
    "Получение трассы"
    route_instance = await crud_route.get(session, route_id)
    if route_instance is None:
        raise HTTPException(404)
    route_instance.set_absolute_image_urls(request)
    return route_instance


@router.delete(
    "/{route_id}",
    name="routes:delete_route",
    responses={**responses.LOGIN_REQUIRED, **responses.ID_NOT_FOUND},
    status_code=204,
)
async def delete_route(
    route_id: UUID = Path(...),
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    "Удаление трассы"
    route_instance = await crud_route.get(session, route_id)
    if route_instance:
        if route_instance.author_id == user.id or user.is_superuser:
            await crud_route.remove(session, row_id=route_id)
            return Response(status_code=204)
        raise HTTPException(
            403, detail="Вы не создатель этой трассы и не администратор"
        )
    raise HTTPException(404)


@router.post(
    "",
    response_model=RouteReadWithAll,
    status_code=201,
    name="routes:new",
    responses=responses.LOGIN_REQUIRED,
)
async def create_route(
    request: Request,
    name: str = Form(..., min_length=1, max_length=150),
    category: Category = Form(...),
    mark_color: str = Form(..., min_length=4, max_length=100),
    description: str = Form("", min_length=0, max_length=10000),
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
            author=user,
            description=description,
            creation_date=creation_date,
            images=images,
        )
        created_route = await crud_route.create(session, route_instance)
        created_route.set_absolute_image_urls(request)
        return created_route
    except ValidationError as err:
        raise RequestValidationError(err.raw_errors) from err
