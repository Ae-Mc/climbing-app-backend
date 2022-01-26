from typing import List

from fastapi_users_db_sqlmodel import Field

from climbing.db.models import RouteImage

from .user_and_route_base_read_classes import RouteRead, UserRead


class RouteReadWithUploader(RouteRead):
    """Модель для чтения трассы с полем uploader"""

    uploader: UserRead = Field(title="Пользователь, загрузивший трассу")


class RouteReadWithImages(RouteRead):
    """Модель для чтения трассы с полем images"""

    images: List[RouteImage] = Field(
        default=[], title="Список изображений трассы"
    )


class RouteReadWithAll(RouteReadWithUploader, RouteReadWithImages):
    """Модель для чтения трассы со всеми дополнительными полями"""
