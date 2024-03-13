import smtplib
from email.mime.text import MIMEText
from typing import Annotated, Any
from uuid import UUID

from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users import InvalidPasswordException
from fastapi_users.exceptions import UserAlreadyExists
from fastapi_users.manager import BaseUserManager, UUIDIDMixin

from climbing.core.config import settings
from climbing.db.models import User, UserCreate
from climbing.db.session import get_user_db
from climbing.db.user_database import UserDatabase


class UserManager(UUIDIDMixin, BaseUserManager[User, UUID]):
    """User manager from fastapi_users"""

    user_db: UserDatabase
    reset_password_token_secret = settings.SECRET
    verification_token_secret = settings.SECRET

    async def authenticate(self, credentials: OAuth2PasswordRequestForm) -> User | None:
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
            await self.user_db.update(user, {"hashed_password": updated_password_hash})

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
            user_create.model_dump(
                exclude_unset=True,
                exclude={
                    "id",
                    "is_superuser",
                    "is_active",
                    "is_verified",
                    "oauth_accounts",
                },
            )
            if safe
            else user_create.model_dump(exclude_unset=True, exclude={"id"})
        )

        user_dict["hashed_password"] = hashed_password
        created_user = await self.user_db.create(user_dict)

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
        validated_update_dict = {}
        for field, value in update_dict.items():
            await self._update_field(validated_update_dict, user, field, value)
        return await self.user_db.update(user, validated_update_dict)

    async def _update_field(
        self, update_dict: dict[str, Any], user: User, field: str, value: Any
    ) -> None:
        if field == "username" and value != user.username:
            existing_user = await self.user_db.get_by_username(value)
            if existing_user is not None:
                raise UserAlreadyExists()
            update_dict["username"] = value
        elif field == "email" and value != user.email:
            existing_user = await self.user_db.get_by_email(value)
            if existing_user is not None:
                raise UserAlreadyExists()
            update_dict["email"] = value
            update_dict["is_verified"] = False
        elif field == "password" and value is not None:
            await self.validate_password(value, user)
            update_dict["hashed_password"] = self.password_helper.hash(value)
        else:
            update_dict[field] = value

    async def validate_password(self, password: str, user: UserCreate | User) -> None:
        if len(password) < 8:
            raise InvalidPasswordException(
                "Пароль слишком короткий: минимум 8 символов"
            )
        return await super().validate_password(password, user)

    async def on_after_forgot_password(
        self, user: User, token: str, request: Request | None = None
    ) -> None:
        server = smtplib.SMTP_SSL(settings.MAIL_SMTP_HOST, settings.MAIL_SMTP_PORT)
        server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
        msg = MIMEText(
            f"""Для сброса пароля пройдите по ссылке: https://climbing.ae-mc.ru/#/password-reset/{token}
Или введите токен сброса пароля вручную:
{token}"""
        )
        msg["Subject"] = "Сброс пароля"
        server.send_message(
            msg,
            from_addr=settings.MAIL_USERNAME,
            to_addrs=user.email,
        )
        return await super().on_after_forgot_password(user, token, request)


def get_user_manager(
    user_db=Depends(get_user_db),
) -> UserManager:
    """Returns UserManager instance

    Returns:
        UserManager: UserManager
    """
    return UserManager(user_db)


UserManagerDep = Annotated[UserManager, Depends(get_user_manager)]
