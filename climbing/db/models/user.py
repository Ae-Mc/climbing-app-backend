from datetime import datetime
from typing import List

from fastapi_users import models
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
    created_at: datetime | None
    oauth_accounts: List[OAuthAccount] = Relationship()


class UserCreate(
    models.BaseUserCreate, __UserWithFullName, __UserWithUsername
):
    """User's creation pydantic scheme"""


class UserUpdate(models.BaseUserUpdate, __UserWithFullName):
    """User's update pydantic scheme"""


class UserScheme(
    models.BaseOAuthAccountMixin,
    models.BaseUserDB,
    __UserWithFullName,
    __UserWithUsername,
):
    """User returning pydantic scheme"""


class RouteUploader(__UserWithUsername, __UserWithFullName):
    id: int
