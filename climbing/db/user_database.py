from fastapi_users_db_sqlmodel import SQLModelUserDatabaseAsync, selectinload
from pydantic import UUID4
from sqlalchemy import select

from climbing.db.models.user import OAuthAccount, User


class UserDatabase(SQLModelUserDatabaseAsync[User, OAuthAccount]):
    """
    Database adapter for SQLModel working purely asynchronously.

    :param user_db_model: SQLModel model of a DB representation of a user.
    :param session: SQLAlchemy async session.
    """

    # pylint: disable=redefined-builtin
    async def get(self, id: UUID4) -> User | None:
        statement = (
            select(self.user_db_model)
            .options(
                selectinload(self.user_db_model.routes),
                selectinload(self.user_db_model.oauth_accounts),
            )
            .where(self.user_db_model.id == id)
        )
        return (await self.session.execute(statement)).scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        """Get user by username"""
        statement = select(self.user_db_model).where(
            self.user_db_model.username == username
        )
        return (await self.session.execute(statement)).scalar_one_or_none()

    async def update(self, user: User) -> User:
        """Update a user."""
        self.session.add(user)
        if self.oauth_account_model is not None:
            user: User = (
                await self.session.execute(
                    select(User)
                    .options(selectinload(User.oauth_accounts))
                    .where(User.id == user.id)
                )
            ).scalar_one()
            for oauth_account in user.oauth_accounts:  # type: ignore
                self.session.add(oauth_account)
        await self.session.commit()
        await self.session.refresh(user)
        return user
