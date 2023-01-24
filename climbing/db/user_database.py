from fastapi_users_db_sqlmodel import SQLModelUserDatabaseAsync, selectinload
from pydantic import UUID4
from sqlalchemy import select

from climbing.db.models.user import OAuthAccount, User


class UserDatabase(SQLModelUserDatabaseAsync[User, OAuthAccount]):
    """
    Database adapter for SQLModel working purely asynchronously.

    :param user_model: SQLModel model of a DB representation of a user.
    :param session: SQLAlchemy async session.
    """

    oauth_account_model = OAuthAccount
    user_model = User

    # pylint: disable=redefined-builtin
    async def get(self, id: UUID4) -> User | None:
        statement = (
            select(self.user_model)
            .options(
                selectinload(self.user_model.routes),
                selectinload(self.user_model.oauth_accounts),
            )
            .where(self.user_model.id == id)
        )
        return (await self.session.execute(statement)).scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        """Get user by username"""
        statement = select(self.user_model).where(
            self.user_model.username == username
        )
        return (await self.session.execute(statement)).scalar_one_or_none()
