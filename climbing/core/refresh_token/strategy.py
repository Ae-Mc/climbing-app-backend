from typing import Generic

from fastapi_users import BaseUserManager
from fastapi_users.authentication.strategy import Strategy
from fastapi_users.models import ID, UP

from climbing.core.refresh_token.db.models import AccessTokenProtocolExtended


class StrategyExtended(Strategy[UP, ID], Generic[UP, ID]):
    async def read_token(
        self,
        token: str | None,
        user_manager: BaseUserManager[UP, ID],
        refresh_token: str | None = None,
    ) -> UP | None: ...  # pragma: no cover

    async def write_token(
        self, user: UP
    ) -> AccessTokenProtocolExtended: ...  # pragma: no cover

    async def destroy_token(
        self, token: str | None, user: UP, refresh_token: str | None = None
    ) -> None: ...  # pragma: no cover
