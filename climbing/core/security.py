from fastapi import Depends
from fastapi_users import FastAPIUsers
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
from climbing.db.models.user import (
    AccessToken,
    User,
    UserCreate,
    UserScheme,
    UserUpdate,
)
from climbing.db.session import get_access_token_db

bearer_transport = BearerTransport(settings.AUTH_TOKEN_ENDPOINT_URL)


def get_strategy(
    access_token_db: AccessTokenDatabase[AccessToken] = Depends(
        get_access_token_db
    ),
) -> Strategy:
    """Returns JWTStrategy used by AuthenticationBackend"""
    return DatabaseStrategy(
        database=access_token_db,
        lifetime_seconds=int(
            settings.ACCESS_TOKEN_EXPIRE_TIME.total_seconds()
        ),
    )


auth_backend = AuthenticationBackend[UserCreate, User](
    name="bearer_database",
    transport=bearer_transport,
    get_strategy=get_strategy,
)

fastapi_users = FastAPIUsers(
    auth_backends=[auth_backend],
    get_user_manager=get_user_manager,
    user_create_model=UserCreate,
    user_db_model=User,
    user_model=UserScheme,
    user_update_model=UserUpdate,
)

current_user = fastapi_users.current_user()
current_active_user = fastapi_users.current_user(active=True)
current_active_verified_user = fastapi_users.current_user(
    active=True, verified=True
)
current_superuser = fastapi_users.current_user(superuser=True)
