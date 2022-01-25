from fastapi_users_db_sqlmodel import SQLModelUserDatabaseAsync
from sqlalchemy import select

from climbing.db.models.user import OAuthAccount, User


class UserDatabase(SQLModelUserDatabaseAsync[User, OAuthAccount]):
    async def get_by_username(self, username: str) -> User | None:
        statement = select(self.user_db_model).where(
            self.user_db_model.username == username
        )
        return (await self.session.execute(statement)).scalar_one_or_none()
