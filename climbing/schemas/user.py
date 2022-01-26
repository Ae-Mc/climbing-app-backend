from typing import List

from fastapi_users_db_sqlmodel import Field

from climbing.db.models.user import OAuthAccount

from .user_and_route_base_read_classes import RouteRead, UserRead


class UserReadWithRoutes(UserRead):
    routes: List[RouteRead] = Field(title="Список трасс пользователя")
