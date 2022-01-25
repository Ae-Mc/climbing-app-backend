from datetime import datetime, timezone
from typing import List

from fastapi_users import models
from fastapi_users_db_sqlalchemy import UUID4
from fastapi_users_db_sqlmodel import (
    Field,
    SQLModelBaseOAuthAccount,
    SQLModelBaseUserDB,
)
from fastapi_users_db_sqlmodel.access_token import SQLModelBaseAccessToken
from sqlmodel import Relationship, SQLModel


class AccessToken(SQLModelBaseAccessToken, table=True):
    """Table for storing access tokens"""


class OAuthAccount(SQLModelBaseOAuthAccount, table=True):
    """Table for storing OAuth accounts for each user"""


class __UserWithFullName(SQLModel):
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)


class __UserWithUsername(SQLModel):
    username: str = Field(max_length=100)


class User(SQLModelBaseUserDB, __UserWithFullName, table=True):
    """User fetch pydantic model"""

    username: str = Field(
        max_length=100, sa_column_kwargs={"unique": True, "index": True}
    )
    created_at: datetime | None = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    oauth_accounts: List[OAuthAccount] = Relationship()


class UserCreate(
    __FullNameMixin, __UsernameMixin, models.CreateUpdateDictModel
):
    """User's creation scheme"""

    email: str
    password: str

class UserUpdate(models.BaseUserUpdate, __UserWithFullName):
    """User's update pydantic scheme"""


class UserScheme(
    __UserWithFullName,
    __UserWithUsername,
    SQLModel,
):
    """User returning pydantic scheme"""

    id: UUID4 | None
    email: str
    created_at: datetime | None

class RouteUploader(__UserWithUsername, __UserWithFullName):
    id: int
