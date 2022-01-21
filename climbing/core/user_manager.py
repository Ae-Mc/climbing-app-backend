from fastapi import Depends, Request
from fastapi_users.manager import BaseUserManager

from climbing.db.session import get_user_db
from climbing.schemas import UserCreate, UserDB

from .private import SECRET


class UserManager(BaseUserManager[UserCreate, UserDB]):
    """User manager from fastapi_users"""

    user_db_model = UserDB
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: UserDB, _: Request = None) -> None:
        print(f"User {user.username} has registered. His id: {user.id}")

    async def on_after_forgot_password(
        self, user: UserDB, token: str, _: Request = None
    ):
        print(
            f"User {user.id} has forgot their password. Reset token: {token}"
        )

    async def on_after_request_verify(
        self, user: UserDB, token: str, _: Request = None
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
