from datetime import datetime

from fastapi_users_db_sqlmodel import Field
from pydantic import UUID4

from climbing.db.models import RouteBase, UserBaseWithCreatedAt


class UserRead(UserBaseWithCreatedAt):
    """User returning pydantic scheme"""

    id: UUID4
    email: str


class RouteRead(RouteBase):
    """Базовая модель для чтения трассы"""

    id: UUID4 = Field(title="ID трассы")
    created_at: datetime = Field(title="Дата добавления трассы на сервер")
