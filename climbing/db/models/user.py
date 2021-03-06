from datetime import datetime, timezone
from typing import TYPE_CHECKING, List

from fastapi import Request
from fastapi_users import models
from fastapi_users_db_sqlmodel import (
    EmailStr,
    Field,
    SQLModelBaseOAuthAccount,
    SQLModelBaseUserDB,
)
from fastapi_users_db_sqlmodel.access_token import SQLModelBaseAccessToken
from sqlmodel import Relationship, SQLModel

if TYPE_CHECKING:
    from climbing.db.models.ascent import Ascent
    from climbing.db.models.route import Route


class AccessToken(SQLModelBaseAccessToken, table=True):
    """Table for storing access tokens"""


class OAuthAccount(SQLModelBaseOAuthAccount, table=True):
    """Table for storing OAuth accounts for each user"""


class CreatedAt(SQLModel):
    """Model with only created_at field"""

    created_at: datetime | None = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class Email(SQLModel):
    """Model with only email field"""

    email: EmailStr = Field()


class FirstAndLastNames(SQLModel):
    """Model with only first_name and last_name fields"""

    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)


class Password(SQLModel):
    """Model with only password field"""

    password: str = Field(default=None, max_length=100)


class Username(SQLModel):
    """Model with only username field"""

    username: str = Field(
        min_length=2,
        max_length=100,
        sa_column_kwargs={"unique": True, "index": True},
    )


class UserBase(FirstAndLastNames, Username):
    """Basic user model, that will be inherited by other models"""


class UserBaseWithCreatedAt(UserBase, CreatedAt):
    """Basic user model with generated created_at field"""


class User(UserBaseWithCreatedAt, SQLModelBaseUserDB, table=True):
    """User model"""

    ascents: List["Ascent"] = Relationship(
        back_populates="user",
        # Instruct the ORM how to track changes to local objects
        sa_relationship_kwargs={"cascade": "delete"},
    )
    oauth_accounts: List[OAuthAccount] = Relationship()
    routes: List["Route"] = Relationship(back_populates="author")

    def set_absolute_image_urls(self, request: Request) -> None:
        """?????????????????????????? ????????????????????, ?? ???? ?????????????????????????? URL-???????????? ??????
        ?????????????????????? ??????????"""

        for route in self.routes:  # pylint: disable=not-an-iterable
            route.set_absolute_image_urls(request)

    def __hash__(self):
        return hash(
            (
                self.id,
                self.first_name,
                self.last_name,
                self.username,
                self.created_at,
                self.email,
                self.is_active,
                self.is_superuser,
                self.is_verified,
            )
        )


class UserCreate(UserBase, Email, Password, models.CreateUpdateDictModel):
    """User's creation scheme"""


class UserUpdate(FirstAndLastNames, Password, models.CreateUpdateDictModel):
    """User's update scheme"""

    oauth_accounts: List[OAuthAccount] | None = None
