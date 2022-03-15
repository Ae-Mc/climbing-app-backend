from datetime import datetime, timezone
from typing import TYPE_CHECKING, List

from fastapi import Request
from fastapi_users import models
from fastapi_users_db_sqlmodel import (
    Field,
    SQLModelBaseOAuthAccount,
    SQLModelBaseUserDB,
)
from fastapi_users_db_sqlmodel.access_token import SQLModelBaseAccessToken
from sqlmodel import Relationship, SQLModel

if TYPE_CHECKING:
    from climbing.db.models.route import Route


class AccessToken(SQLModelBaseAccessToken, table=True):
    """Table for storing access tokens"""


class OAuthAccount(SQLModelBaseOAuthAccount, table=True):
    """Table for storing OAuth accounts for each user"""


class UserBase(SQLModel):
    """Basic user model, that will be inherited by other models"""

    username: str = Field(
        max_length=100, sa_column_kwargs={"unique": True, "index": True}
    )
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)

    created_at: datetime | None = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class User(UserBase, SQLModelBaseUserDB, table=True):
    """User model"""

    oauth_accounts: List[OAuthAccount] = Relationship()
    routes: List["Route"] = Relationship(back_populates="author")

    def set_absolute_image_urls(self, request: Request) -> None:
        """Устанавливает абсолютные, а не относительные URL-адреса для
        изображений трасс"""

        for route in self.routes:  # pylint: disable=not-an-iterable
            route.set_absolute_image_urls(request)


class UserCreate(UserBase, models.CreateUpdateDictModel):
    """User's creation scheme"""

    email: str = Field(max_length=100)
    password: str = Field(max_length=100)


class UserUpdate(models.CreateUpdateDictModel):
    """User's update scheme"""

    password: str | None = Field(default=None, max_length=100)
    first_name: str | None = Field(default=None, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)
    oauth_accounts: List[OAuthAccount] | None = None
