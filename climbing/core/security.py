from typing import Annotated
from uuid import UUID

from fastapi import Depends
from fastapi_users import FastAPIUsers
from fastapi_users.authentication.backend import AuthenticationBackendRefresh
from fastapi_users.authentication.strategy import (
    AccessRefreshTokenDatabase,
    StrategyRefresh,
)
from fastapi_users.authentication.strategy.db import DatabaseRefreshStrategy
from fastapi_users.authentication.transport import BearerTransportRefresh

from climbing.core.config import settings
from climbing.core.user_manager import get_user_manager
from climbing.db.models import AccessRefreshToken, User, UserCreate
from climbing.db.session import get_access_token_db

bearer_transport = BearerTransportRefresh(settings.AUTH_TOKEN_ENDPOINT_URL)


def get_strategy(
    access_token_db: AccessRefreshTokenDatabase[AccessRefreshToken] = Depends(
        get_access_token_db
    ),
) -> StrategyRefresh:
    """Returns Strategy used by AuthenticationBackend"""
    return DatabaseRefreshStrategy(
        database=access_token_db,
        lifetime_seconds=int(settings.ACCESS_TOKEN_EXPIRE_TIME.total_seconds()),
        refresh_lifetime_seconds=int(
            settings.REFRESH_TOKEN_EXPIRE_TIME.total_seconds()
        ),
    )


StrategyDep = Annotated[StrategyRefresh, Depends(get_strategy)]


auth_backend = AuthenticationBackendRefresh[UserCreate, User](  # type: ignore
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
current_active_verified_user = fastapi_users.current_user(active=True, verified=True)
current_superuser = fastapi_users.current_user(superuser=True)

CurrentActiveUserDep = Annotated[User, Depends(current_active_user)]
CurrentSuperuser = Annotated[User, Depends(current_superuser)]
