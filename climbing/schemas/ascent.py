from climbing.schemas.route import RouteReadWithAll

from .base_read_classes import AscentRead, UserRead


class AscentReadWithAll(AscentRead):
    """Чтение подъёма со всеми возможными параметрами"""

    user: UserRead
    route: RouteReadWithAll
