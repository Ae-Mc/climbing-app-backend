from typing import List

from pydantic import Field

from climbing.db.models import RouteImage
from climbing.db.models.route import RouteBase

from .base_read_classes import RouteRead, UserRead


class RouteCreateSchema(RouteBase):
    author_id: None = Field(
        None, title="Ignore field, will be filled automatically", exclude=True
    )


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
