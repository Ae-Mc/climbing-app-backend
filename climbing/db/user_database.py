from fastapi_users_db_sqlmodel import SQLModelUserDatabaseAsync, selectinload
from sqlalchemy import select

from climbing.db.models.user import OAuthAccount, User


class UserDatabase(SQLModelUserDatabaseAsync[User, OAuthAccount]):
    async def get_by_username(self, username: str) -> User | None:
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
