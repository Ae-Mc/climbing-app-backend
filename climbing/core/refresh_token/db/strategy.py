import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Generic

from fastapi_users import BaseUserManager, exceptions
from fastapi_users.authentication.strategy.db import DatabaseStrategy
from fastapi_users.models import ID, UP

from climbing.core.refresh_token.db.adapter import AccessRefreshTokenDatabase
from climbing.core.refresh_token.strategy import StrategyExtended

from .models import APE, AccessTokenProtocolExtended


class DatabaseStrategyExtended(
    DatabaseStrategy[UP, ID, APE],
    StrategyExtended[UP, ID],
    Generic[UP, ID, APE],
):
    database: AccessRefreshTokenDatabase[APE]
    refresh_lifetime_seconds: int | None

    def __init__(
        self,
        database: AccessRefreshTokenDatabase[APE],
        lifetime_seconds: int | None = None,
        refresh_lifetime_seconds: int | None = None,
    ):
        super().__init__(database, lifetime_seconds)
        self.refresh_lifetime_seconds = refresh_lifetime_seconds

    async def read_token(
        self,
        token: str | None,
        user_manager: BaseUserManager[UP, ID],
        refresh_token: str | None = None,
    ) -> UP | None:
        if token is not None:
            return await super().read_token(token, user_manager)
        max_age = None
        if self.refresh_lifetime_seconds:
            max_age = datetime.now(timezone.utc) - timedelta(
                seconds=self.refresh_lifetime_seconds
            )
        access_token = await self.database.get_by_refresh_token(
            refresh_token=refresh_token, max_age=max_age
        )
        if access_token is None:
            return None
        try:
            parsed_id = user_manager.parse_id(access_token.user_id)
            return await user_manager.get(parsed_id)
        except (exceptions.UserNotExists, exceptions.InvalidID):
            return None

    async def write_token(self, user: UP) -> AccessTokenProtocolExtended:
        access_token_dict = self._create_access_token_dict(user)
        return await self.database.create(access_token_dict)

    async def destroy_token(
        self, token: str | None, user: UP, refresh_token: str | None = None
    ) -> None:
        if token is not None:
            return await super().destroy_token(token, user)
        access_token = await self.database.get_by_refresh_token(
            refresh_token=refresh_token
        )
        if access_token is not None:
            await self.database.delete(access_token)

    def _create_access_token_dict(self, user: UP) -> Dict[str, Any]:
        token_dict = super()._create_access_token_dict(user)
        refresh_token = secrets.token_urlsafe()
        token_dict["refresh_token"] = refresh_token
        return token_dict
