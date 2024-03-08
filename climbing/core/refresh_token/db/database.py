from datetime import datetime
from typing import Generic

from fastapi_users_db_sqlmodel.access_token import (
    SQLModelAccessTokenDatabaseAsync,
)
from sqlmodel import select

from .adapter import AccessRefreshTokenDatabase
from .models import APE


class SQLModelAccessRefreshTokenDatabaseAsync(
    SQLModelAccessTokenDatabaseAsync[APE],
    AccessRefreshTokenDatabase[APE],
    Generic[APE],
):
    async def get_by_refresh_token(
        self, refresh_token: str, max_age: datetime | None = None
    ) -> APE | None:
        statement = select(self.access_token_model).where(  # type: ignore
            self.access_token_model.refresh_token == refresh_token
        )
        if max_age is not None:
            statement = statement.where(
                self.access_token_model.created_at >= max_age
            )

        results = await self.session.execute(statement)
        access_token = results.first()
        if access_token is None:
            return None

        return access_token[0]
