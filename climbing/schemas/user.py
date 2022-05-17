from typing import List

from fastapi_users_db_sqlmodel import Field

from .base_read_classes import RouteRead, UserRead


class UserReadWithRoutes(UserRead):
    routes: List[RouteRead] = Field(title="Список трасс пользователя")
