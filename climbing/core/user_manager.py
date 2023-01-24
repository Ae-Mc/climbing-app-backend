from typing import Any
from uuid import UUID

from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users import InvalidPasswordException
from fastapi_users.exceptions import UserAlreadyExists
from fastapi_users.manager import BaseUserManager, UUIDIDMixin

from climbing.db.models import User, UserCreate
from climbing.db.session import get_user_db
from climbing.db.user_database import UserDatabase

from .private import SECRET


class UserManager(UUIDIDMixin, BaseUserManager[User, UUID]):
    """User manager from fastapi_users"""

    user_db: UserDatabase
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def authenticate(
        self, credentials: OAuth2PasswordRequestForm
    ) -> User | None:
        user = await self.get_user_by_credentials(credentials)
        if user is None:
            # Run the hasher to mitigate timing attack
            # Inspired from Django: https://code.djangoproject.com/ticket/20760
            self.password_helper.hash(credentials.password)
            return None

        (
            verified,
            updated_password_hash,
        ) = self.password_helper.verify_and_update(
            credentials.password, user.hashed_password
        )
        if not verified:
            return None
        # Update password hash to a more robust one if needed
        if updated_password_hash is not None:
            user.hashed_password = updated_password_hash
            await self.user_db.update(user)

        return user

    async def get_user_by_credentials(
        self, credentials: OAuth2PasswordRequestForm
    ) -> User | None:
        """Returns user, if exists, from OAuth сredentials

        Here you can add e.g. phone number or username search.
        """
        user = await self.user_db.get_by_username(credentials.username)
        if user is not None:
            return user
        # We can add any more tests using the same code
        user = await self.user_db.get_by_email(credentials.username)
        if user is not None:
            return user
        return None

    async def create(
        self,
        user_create: UserCreate,
        safe: bool = False,
        request: Request | None = None,
    ) -> User:
        await self.validate_password(user_create.password, user_create)

        await self.test_user_existence(user_create)

        hashed_password = self.password_helper.hash(user_create.password)
        user_dict = (
            user_create.create_update_dict()
            if safe
            else user_create.create_update_dict_superuser()
        )
        db_user = User(
            **user_dict, hashed_password=hashed_password
        )
        created_user = await self.user_db.create(db_user)

        await self.on_after_register(created_user, request)

        return created_user

    async def test_user_existence(self, user: UserCreate) -> None:
        """Tests if user with the same data as :param user: exists

        :raises UserAlreadyExists: The user exists.
        """
        if await self.user_db.get_by_username(user.username) is not None:
            raise UserAlreadyExists()
        if await self.user_db.get_by_email(user.email) is not None:
            raise UserAlreadyExists()

    async def _update(self, user: User, update_dict: dict[str, Any]) -> User:
        for field, value in update_dict.items():
            await self._update_field(user, field, value)
        return await self.user_db.update(user, update_dict)

    async def _update_field(self, user: User, field: str, value: Any) -> None:
        if field == "username" and value != user.username:
            existing_user = await self.user_db.get_by_username(value)
            if existing_user is not None:
                raise UserAlreadyExists()
            user.username = value
        elif field == "email" and value != user.email:
            existing_user = await self.user_db.get_by_email(value)
            if existing_user is not None:
                raise UserAlreadyExists()
            user.email = value
            user.is_verified = False
        elif field == "password":
            await self.validate_password(value, user)
            hashed_password = self.password_helper.hash(value)
            user.hashed_password = hashed_password
        else:
            setattr(user, field, value)

    async def validate_password(
        self, password: str, user: UserCreate | User
    ) -> None:
        if len(password) < 8:
            raise InvalidPasswordException(
                "Пароль слишком короткий: минимум 8 символов"
            )
        return await super().validate_password(password, user)


def get_user_manager(
    user_db=Depends(get_user_db),
) -> UserManager:
    """Returns UserManager instance

    Returns:
        UserManager: UserManager
    """
    return UserManager(user_db)
