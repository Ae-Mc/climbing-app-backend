from datetime import datetime

from fastapi_users import models
from fastapi_users.authentication.strategy.db import BaseAccessToken


class User(models.BaseUser, models.BaseOAuthAccountMixin):
    """User fetch pydantic model"""

    username: str
    first_name: str
    last_name: str
    creation_date: datetime


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
