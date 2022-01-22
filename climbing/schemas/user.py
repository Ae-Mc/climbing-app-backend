from datetime import datetime
from uuid import UUID

from fastapi_users import models
from fastapi_users.authentication.strategy.db import BaseAccessToken
from pydantic import BaseModel


class User(models.BaseUser, models.BaseOAuthAccountMixin):
    """User fetch pydantic model"""

    username: str
    first_name: str
    last_name: str
    created_at: datetime | None

    # pylint: disable=too-few-public-methods,missing-class-docstring
    class Config:
        orm_mode = True


class UserCreate(models.BaseUserCreate):
    """User's creation pydantic scheme"""

    username: str
    first_name: str
    last_name: str


class UserUpdate(models.BaseUserUpdate):
    """User's update pydantic scheme"""

    first_name: str
    last_name: str


class UserDB(User, models.BaseUserDB):
    """User stored in DB pydantic model"""


class AccessToken(BaseAccessToken):
    """Access token pydantic model"""


class RouteUploader(BaseModel):
    id: UUID
    username: str
    first_name: str
    last_name: str

    # pylint: disable=too-few-public-methods,missing-class-docstring
    class Config:
        orm_mode = True
