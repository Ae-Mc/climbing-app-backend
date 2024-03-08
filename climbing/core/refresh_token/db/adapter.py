from datetime import datetime
from typing import Generic

from fastapi_users.authentication.strategy.db.adapter import (
    AccessTokenDatabase,
)

from climbing.core.refresh_token.db.models import APE


class AccessRefreshTokenDatabase(AccessTokenDatabase[APE], Generic[APE]):
    async def get_by_refresh_token(
        self, refresh_token: str, max_age: datetime | None = None
    ) -> APE | None:
        """Get a single access token by refresh token"""
        ...
