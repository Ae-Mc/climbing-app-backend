from pydantic import Field

from climbing.schemas.route import RouteReadWithAll

from .base_read_classes import AscentRead, UserRead


class AscentReadWithRoute(AscentRead):
    """Чтение пролаза трассой"""

    route: RouteReadWithAll = Field(..., title="Трасса")


class AscentReadWithAll(AscentReadWithRoute):
    """Чтение пролаза со всеми возможными параметрами"""

    user: UserRead = Field(..., title="Скалолаз")
