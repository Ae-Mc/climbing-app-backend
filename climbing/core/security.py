from contextlib import aclosing
from typing import Annotated, AsyncGenerator
from uuid import UUID

from fastapi import Depends
from fastapi_users import FastAPIUsers
from fastapi_users.authentication.strategy.db import AccessTokenDatabase

from climbing.core.config import settings
from climbing.core.refresh_token.backend import AuthenticationBackendRefresh
from climbing.core.refresh_token.db.strategy import DatabaseStrategyExtended
from climbing.core.refresh_token.strategy import StrategyExtended
from climbing.core.refresh_token.transport import BearerTransportRefresh
from climbing.core.user_manager import get_user_manager
from climbing.db.models import AccessRefreshToken, User, UserCreate
from climbing.db.session import get_access_token_db

bearer_transport = BearerTransportRefresh(settings.AUTH_TOKEN_ENDPOINT_URL)


def get_strategy(
    access_token_db: AccessTokenDatabase[AccessRefreshToken] = Depends(
        get_access_token_db
    ),
) -> StrategyExtended:
    """Returns Strategy used by AuthenticationBackend"""
    return DatabaseStrategyExtended(
        database=access_token_db,
        lifetime_seconds=int(settings.ACCESS_TOKEN_EXPIRE_TIME.total_seconds()),
        refresh_lifetime_seconds=int(
            settings.REFRESH_TOKEN_EXPIRE_TIME.total_seconds()
        ),
    )


StrategyDep = Annotated[StrategyExtended, Depends(get_strategy)]


auth_backend = AuthenticationBackendRefresh[UserCreate, User](
    name="bearer_database",
    transport=bearer_transport,
    get_strategy=get_strategy,
)

fastapi_users = FastAPIUsers[User, UUID](
    get_user_manager=get_user_manager,
    auth_backends=[auth_backend],
)

current_user = fastapi_users.current_user()
current_active_user = fastapi_users.current_user(active=True)
current_active_verified_user = fastapi_users.current_user(
    active=True, verified=True
)
current_superuser = fastapi_users.current_user(superuser=True)

CurrentActiveUserDep = Annotated[User, Depends(current_active_user)]
CurrentSuperuser = Annotated[User, Depends(current_superuser)]
