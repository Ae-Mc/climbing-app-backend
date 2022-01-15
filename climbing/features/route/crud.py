from ntpath import join
from os import makedirs, mkdir
from shutil import copyfileobj
from typing import List
from fastapi import UploadFile
from sqlalchemy.orm import Session

from core.db.model import File as DBFile
from core.db.model import Route as DBRoute
from core.db.model import RouteImage as DBImage

from .model import RouteCreate


def get_routes(database: Session):
    """Get all routes from database"""
    return database.query(DBRoute).all()


def get_route(database: Session, route_id: int):
    """Get route from database by id"""
    return database.query(DBRoute).filter(DBRoute.id == route_id).first()


def create_route(
    database: Session,
    uploader_id: int,
    route: RouteCreate,
    images: List[UploadFile],
):
    """Add route to database"""
    db_route = DBRoute(
        name=route.name,
        category=route.category,
        mark_color=route.mark_color,
        author=route.author,
        uploader_id=uploader_id,
        descrition=route.description,
        creation_date=route.creation_date,
    )
    database.add(db_route)
    database.commit()
    database.refresh(db_route)
    db_images: List[DBImage] = []
    if len(images) > 0:
        route_images_path = f"media/routes/{db_route.id}/images"
        makedirs(route_images_path)
        for index, image in enumerate(images):
            current_image_folder_path = join(route_images_path, str(index))
            current_image_path = join(
                current_image_folder_path, image.filename
            )
            mkdir(current_image_folder_path)
            with open(
                current_image_path,
                "wb",
            ) as image_file:
                copyfileobj(image.file, image_file)
                db_images.append(
                    DBFile(
                        url=current_image_path,
                        uploader_id=uploader_id,
                    )
                )

    database.add_all(db_images)
    database.commit()
    for image in db_images:
        database.refresh(image)
        database.add(DBImage(route_id=db_route.id, image_id=image.id))
    database.commit()
    database.refresh(db_route)

    return db_route
