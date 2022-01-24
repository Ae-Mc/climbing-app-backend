from fastapi import Depends, Request
from fastapi_users.manager import BaseUserManager

from climbing.db.models import User, UserCreate
from climbing.db.session import get_user_db

from .private import SECRET


class UserManager(BaseUserManager[UserCreate, User]):
    """User manager from fastapi_users"""

    user_db_model = User
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, _: Request = None) -> None:
        print(f"User {user.username} has registered. His id: {user.id}")

    async def on_after_forgot_password(
        self, user: User, token: str, _: Request = None
    ):
        print(
            f"User {user.id} has forgot their password. Reset token: {token}"
        )

    async def on_after_request_verify(
        self, user: User, token: str, _: Request = None
    ):
        print(
            f"Verification requested for user {user.id}."
            f" Verification token: {token}"
        )


def get_user_manager(
    user_db=Depends(get_user_db),
) -> UserManager:
    """Returns UserManager instance

    Returns:
        UserManager: UserManager
    """
    return UserManager(user_db)
