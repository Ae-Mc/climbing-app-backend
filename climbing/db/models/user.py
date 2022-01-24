from datetime import datetime

from fastapi_users import models
from fastapi_users_db_sqlmodel import (
    SQLModelBaseOAuthAccount,
    SQLModelBaseUserDB,
)
from fastapi_users_db_sqlmodel.access_token import SQLModelBaseAccessToken
from sqlmodel import SQLModel


class User(SQLModelBaseUserDB, table=True):
    """User fetch pydantic model"""

    username: str
    first_name: str
    last_name: str
    created_at: datetime | None


class UserCreate(models.BaseUserCreate, SQLModel):
    """User's creation pydantic scheme"""

    username: str
    first_name: str
    last_name: str


class UserUpdate(models.BaseUserUpdate, SQLModel):
    """User's update pydantic scheme"""

    first_name: str
    last_name: str


class AccessToken(SQLModelBaseAccessToken, table=True):
    """Table for storing access tokens"""


class OAuthAccount(SQLModelBaseOAuthAccount, table=True):
    """Table for storing OAuth accounts for each user"""


class RouteUploader(SQLModel):
    id: int
    username: str
    first_name: str
    last_name: str
