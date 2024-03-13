from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, List

from fastapi import Request
from fastapi_users.schemas import BaseUserCreate, BaseUserUpdate
from fastapi_users_db_sqlmodel import (
    SQLModelBaseOAuthAccount,
    SQLModelBaseUserDB,
)
from fastapi_users_db_sqlmodel.access_token import SQLModelBaseAccessRefreshToken
from pydantic import UUID4, ConfigDict, EmailStr
from sqlmodel import AutoString, Field, ForeignKey, Relationship, SQLModel

if TYPE_CHECKING:
    from climbing.db.models.ascent import Ascent
    from climbing.db.models.route import Route


class AccessRefreshToken(SQLModelBaseAccessRefreshToken, table=True):
    """Table for storing access and refresh tokens"""

    user_id: UUID4 = Field(
        ...,
        sa_column_args=(ForeignKey("user.id", ondelete="CASCADE"),),
        nullable=False,
    )


class OAuthAccount(SQLModelBaseOAuthAccount, table=True):
    """Table for storing OAuth accounts for each user"""

    user_id: UUID4 = Field(
        ...,
        sa_column_args=(ForeignKey("user.id", ondelete="CASCADE"),),
        nullable=False,
    )


class CreatedAt(SQLModel):
    """Model with only created_at field"""

    created_at: datetime | None = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class Email(SQLModel):
    """Model with only email field"""

    email: EmailStr = Field(sa_type=AutoString)


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
        unique=True,
        index=True,
    )


class SexEnum(Enum):
    male = "male"
    female = "female"

    def __str__(self) -> str:
        return self.value


class IsStudent(SQLModel):
    """Model with only is_student field"""

    is_student: bool = Field(False, sa_column_kwargs={"server_default": "0"})


class Sex(SQLModel):
    """Model with only sex field"""

    sex: SexEnum = Field(
        SexEnum.male,
        sa_column_kwargs={"server_default": str(SexEnum.male.value)},
        sa_type=AutoString,
    )

    model_config = ConfigDict(use_enum_values=True)


class UserBase(FirstAndLastNames, Username, IsStudent, Sex):
    """Basic user model, that will be inherited by other models"""


class UserBaseWithCreatedAt(UserBase, CreatedAt):
    """Basic user model with generated created_at field"""


class User(UserBaseWithCreatedAt, SQLModelBaseUserDB, table=True):
    """User model"""

    ascents: List["Ascent"] = Relationship(
        back_populates="user",
        # Instruct the ORM how to track changes to local objects
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    oauth_accounts: List[OAuthAccount] = Relationship()
    routes: List["Route"] = Relationship(back_populates="author")

    def set_absolute_image_urls(self, request: Request) -> None:
        """Устанавливает абсолютные, а не относительные URL-адреса для
        изображений трасс"""

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


class UserCreate(UserBase, Email, Password, BaseUserCreate):
    """User's creation scheme"""


class UserUpdate(FirstAndLastNames, Password, IsStudent, Sex, BaseUserUpdate):
    """User's update scheme"""

    first_name: str | None
    last_name: str | None
    oauth_accounts: List[OAuthAccount] | None = None
