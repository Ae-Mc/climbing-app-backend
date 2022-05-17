from pydantic import Field

from climbing.schemas.route import RouteReadWithAll

from .base_read_classes import AscentRead, UserRead


class AscentReadWithAll(AscentRead):
    """Чтение подъёма со всеми возможными параметрами"""

    user: UserRead = Field(..., title="Скалолаз")
    route: RouteReadWithAll = Field(..., title="Трасса")
