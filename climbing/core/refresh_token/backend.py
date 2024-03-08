from typing import Generic

from fastapi import Response
from fastapi_users import BaseUserManager
from fastapi_users.authentication import AuthenticationBackend
from fastapi_users.models import ID, UP
from fastapi_users.types import DependencyCallable

from climbing.core.refresh_token.strategy import StrategyExtended
from climbing.core.refresh_token.transport import TransportExtended


class AuthenticationBackendRefresh(
    AuthenticationBackend[UP, ID], Generic[UP, ID]
):
    transport: TransportExtended

    def __init__(
        self,
        name: str,
        transport: TransportExtended,
        get_strategy: DependencyCallable[StrategyExtended[UP, ID]],
    ):
        super().__init__(name, transport, get_strategy)

    async def login(
        self, strategy: StrategyExtended[UP, ID], user: UP
    ) -> Response:
        token = await strategy.write_token(user)
        return await self.transport.get_login_response(token)

    async def refresh(
        self,
        strategy: StrategyExtended[UP, ID],
        user_manager: BaseUserManager[UP, ID],
        refresh_token: str,
    ) -> Response | None:
        user = await strategy.read_token(
            None, refresh_token=refresh_token, user_manager=user_manager
        )
        if user is not None:
            await strategy.destroy_token(
                None, user=user, refresh_token=refresh_token
            )
            token = await strategy.write_token(user)
            return await self.transport.get_login_response(token)
