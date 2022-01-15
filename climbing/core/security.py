from fastapi import Depends
from fastapi_users.fastapi_users import FastAPIUsers
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    Strategy,
)
from fastapi_users.authentication.strategy.db import (
    AccessTokenDatabase,
    DatabaseStrategy,
)

from climbing.core.config import settings
from climbing.core.user_manager import get_user_manager
from climbing.db.session import get_access_token_db
from climbing.schemas.user import (
    AccessToken,
    User,
    UserCreate,
    UserDB,
    UserUpdate,
)

bearer_transport = BearerTransport(settings.AUTH_TOKEN_ENDPOINT_URL)


def get_strategy(
    access_token_db: AccessTokenDatabase[AccessToken] = Depends(
        get_access_token_db
    ),
) -> Strategy:
    """Returns JWTStrategy used by AuthenticationBackend"""
    return DatabaseStrategy(
        database=access_token_db, lifetime_seconds=settings
    )


auth_backend = AuthenticationBackend(
    name="bearer_database",
    transport=bearer_transport,
    get_strategy=get_strategy,
)

fastapi_users = FastAPIUsers(
    auth_backends=[auth_backend],
    get_user_manager=get_user_manager,
    user_create_model=UserCreate,
    user_db_model=UserDB,
    user_model=User,
    user_update_model=UserUpdate,
)
