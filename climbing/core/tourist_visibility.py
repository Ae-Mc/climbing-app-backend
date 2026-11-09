"""Правила видимости туристических данных."""

from climbing.db.models.user import User


def may_view_tourists(viewer: User | None) -> bool:
    """Туристические данные доступны только туристам."""
    return viewer is not None and viewer.is_tourist


def rating_tourist_filter(
    viewer: User | None, only_tourists: bool = False
) -> bool | None:
    """Возвращает допустимый фильтр рейтинга для текущего пользователя."""
    if not may_view_tourists(viewer):
        return False
    return True if only_tourists else None
