from datetime import date
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    Path,
    Query,
    Request,
    UploadFile,
)
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.selectable import Select

from climbing.core import responses
from climbing.core.security import current_active_user
from climbing.crud import route as crud_route
from climbing.db.models import Category, RouteCreate, User
from climbing.db.models.route import Route
from climbing.db.session import get_async_session
from climbing.schemas import RouteReadWithAll
from climbing.schemas.base_read_classes import RouteRead
from climbing.schemas.filters.routes_filter import RoutesFilter
from climbing.schemas.route import RouteCreateSchema

router = APIRouter()


@router.get("", response_model=list[RouteReadWithAll], name="routes:all")
async def routes(
    request: Request,
    filter: RoutesFilter = Depends(),
    session: AsyncSession = Depends(get_async_session),
):
    "Получение списка всех трасс"

    def query_modifier(query: Select[Route]) -> Select[Route]:
        if filter.archived is not None:
            query = query.where(Route.archived == filter.archived)
        if filter.author_id is not None:
            query = query.where(Route.author_id == filter.author_id)
        return query

    _routes = await crud_route.get_all(session, query_modifier)
    for _route in _routes:
        _route.set_absolute_image_urls(request)
    return _routes


@router.get(
    "/{route_id}",
    response_model=RouteReadWithAll,
    name="routes:route",
    responses=responses.ID_NOT_FOUND.docs(),
)
async def route(
    request: Request,
    route_id: UUID = Path(...),
    session: AsyncSession = Depends(get_async_session),
):
    "Получение трассы"
    route_instance = await crud_route.get(session, route_id)
    if route_instance is None:
        raise responses.ID_NOT_FOUND.exception()
    route_instance.set_absolute_image_urls(request)
    return route_instance


@router.delete(
    "/{route_id}",
    name="routes:delete_route",
    responses={
        **responses.UNAUTHORIZED.docs(),
        **responses.ID_NOT_FOUND.docs(),
    },
    status_code=204,
)
async def delete_route(
    route_id: UUID = Path(...),
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    "Удаление трассы"
    route_instance = await crud_route.get(session, route_id)
    if route_instance is None:
        raise responses.ID_NOT_FOUND.exception()
    if route_instance.author_id != user.id and not user.is_superuser:
        raise responses.UNAUTHORIZED.exception()
    await crud_route.remove(session, row_id=route_id)


@router.post(
    "/new",
    response_model=RouteReadWithAll,
    status_code=201,
    name="routes:modern_new",
    responses=responses.UNAUTHORIZED.docs(),
    include_in_schema=False,
)
async def create_route_modern(
    request: Request,
    route_instance: RouteCreateSchema = Form(),
    author_id: None = Query(None, include_in_schema=False),
    images: list[UploadFile] = File([], media_type="image/*"),
    author: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    "Создание трассы"
    try:
        route_instance = RouteCreate(
            **route_instance.dict(),
            author=author,
            images=images,
        )
        created_route = await crud_route.create(session, route_instance)
        created_route.set_absolute_image_urls(request)
        return created_route
    except ValidationError as err:
        raise RequestValidationError(err.raw_errors) from err


@router.post(
    "",
    response_model=RouteReadWithAll,
    status_code=201,
    name="routes:new",
    responses=responses.UNAUTHORIZED.docs(),
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


@router.patch(
    "/{route_id}/archive",
    name="routes:archive",
    responses={
        **responses.UNAUTHORIZED.docs(),
        **responses.ID_NOT_FOUND.docs(),
    },
    response_model=RouteReadWithAll,
)
async def archive_route(
    request: Request,
    route_id: UUID = Path(...),
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    obj = await route(request, route_id, session)
    if obj.author_id != user.id and not user.is_superuser:
        raise responses.UNAUTHORIZED.exception()
    obj.archived = True
    updated_obj = await crud_route.update(
        session, db_entity=obj, new_entity=obj
    )
    return updated_obj
