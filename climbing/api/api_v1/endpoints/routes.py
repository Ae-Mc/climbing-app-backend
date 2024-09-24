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
from fastapi_users.exceptions import UserNotExists
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.selectable import Select
from sqlmodel import col

from climbing.core import responses
from climbing.core.security import current_active_user
from climbing.core.user_manager import UserManager, get_user_manager
from climbing.crud import route as crud_route
from climbing.db.models import Category, RouteCreate, User
from climbing.db.models.route import Route, RouteBase, RouteUpdate
from climbing.db.session import get_async_session
from climbing.schemas import RouteReadWithAll
from climbing.schemas.filters.routes_filter import RoutesFilter

router = APIRouter()


@router.get("", response_model=list[RouteReadWithAll], name="routes:all")
async def routes(
    request: Request,
    filter: RoutesFilter = Depends(),
    session: AsyncSession = Depends(get_async_session),
):
    "Получение списка всех трасс"

    def query_modifier(query: Select[tuple[Route]]) -> Select[tuple[Route]]:
        if filter.archived is not None:
            query = query.where(col(Route.archived) == filter.archived)
        if filter.author_id is not None:
            query = query.where(col(Route.author_id) == filter.author_id)
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


@router.put(
    "/{route_id}",
    response_model=RouteReadWithAll,
    name="routes:update",
    responses={
        **responses.ACCESS_DENIED.docs(),
        **responses.UNAUTHORIZED.docs(),
        **responses.ID_NOT_FOUND.docs(),
    },
)
async def update_route(
    request: Request,
    route_id=Path(...),
    new_author_id: UUID | None = Query(None),
    route_obj: RouteBase = Depends(),
    images: list[UploadFile] = File([], media_type="image/*"),
    current_user: User = Depends(current_active_user),
    user_manager: UserManager = Depends(get_user_manager),
    session: AsyncSession = Depends(get_async_session),
) -> RouteReadWithAll:
    """Изменение трассы. Попытка вызвать этот метод в Swagger приводит к ошибке
    — Swagger неправильно выставляет Content-Length"""

    old_db_route = await route(request, route_id, session)
    if not current_user.is_superuser and old_db_route.author_id != current_user.id:
        raise responses.ACCESS_DENIED.exception()
    if new_author_id is None:
        author = old_db_route.author
    else:
        try:
            author = await user_manager.get(new_author_id)
        except UserNotExists:
            raise responses.ID_NOT_FOUND.exception()
    try:
        db_route = RouteUpdate(
            **route_obj.model_dump(),
            author_id=author.id,
            images=images,
        )
        updated_route = await crud_route.update(
            session, db_entity=old_db_route, new_entity=db_route
        )
        updated_route.set_absolute_image_urls(request)
        return RouteReadWithAll.model_validate(updated_route)
    except ValidationError as err:
        raise RequestValidationError(
            err.errors(include_input=False, include_url=False)
        ) from err


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
            author_id=user.id,
            description=description,
            creation_date=creation_date,
            images=images,
        )
        created_route = await crud_route.create(session, route_instance)
        created_route.set_absolute_image_urls(request)
        return created_route
    except ValidationError as err:
        raise RequestValidationError(
            err.errors(include_input=False, include_url=False)
        ) from err


@router.patch(
    "/{route_id}/archive",
    name="routes:archive",
    responses={
        **responses.ACCESS_DENIED.docs(),
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
        raise responses.ACCESS_DENIED.exception()
    updated_obj = await crud_route.archive(session, row_id=obj.id)
    return updated_obj
