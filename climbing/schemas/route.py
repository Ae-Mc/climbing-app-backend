from typing import List

from pydantic import Field

from climbing.db.models import RouteImage

from .base_read_classes import RouteRead, UserRead


class RouteReadWithAuthor(RouteRead):
    """Модель для чтения трассы с полем uploader"""

    author: UserRead = Field(title="Автор трассы")


class RouteReadWithImages(RouteRead):
    """Модель для чтения трассы с полем images"""

    images: List[RouteImage] = Field(
        default=[], title="Список изображений трассы"
    )


class RouteReadWithAll(RouteReadWithAuthor, RouteReadWithImages):
    """Модель для чтения трассы со всеми дополнительными полями"""
