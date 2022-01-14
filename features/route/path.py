from datetime import date
from typing import List

from fastapi import APIRouter, Depends, Form, Path, UploadFile
from sqlalchemy.orm import Session

from core.dependency import get_database
from .crud import get_route, get_routes
from .model import Route, RouteCreate


router = APIRouter(prefix="/routes", tags=["routes"])


@router.get("", response_model=List[Route])
def routes(database: Session = Depends(get_database)):
    """Возвращает список всех трасс"""

    data = get_routes(database)
    return data


@router.post("")
def create_route(
    database: Session = Depends(get_database),
    route: RouteCreate = Form(...),
    files: List[UploadFile] = Form(..., media_type="image/*"),
):
    """Создаёт новую трассу"""
    print(route)
    print(files)


@router.get("/{route_id}", response_model=Route)
def route(
    database: Session = Depends(get_database),
    route_id: int = Path(..., title="ID запрашиваемой трассы"),
):
    """Возвращает трассу с id = route_id"""

    return get_route(database, route_id)
