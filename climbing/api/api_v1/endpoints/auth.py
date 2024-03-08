from typing import Annotated

from fastapi import APIRouter, Body

from climbing.core import responses
from climbing.core.refresh_token.transport import BearerResponseExtended
from climbing.core.security import StrategyDep, auth_backend, fastapi_users
from climbing.core.user_manager import UserManagerDep
from climbing.db.models import UserCreate
from climbing.schemas.base_read_classes import UserRead

router = APIRouter()
router.include_router(fastapi_users.get_auth_router(backend=auth_backend))
router.include_router(fastapi_users.get_register_router(UserRead, UserCreate))
router.include_router(fastapi_users.get_verify_router(UserRead))
router.include_router(fastapi_users.get_reset_password_router())


@router.post(path="/refresh_token", responses=responses.INVALID_TOKEN.docs())
async def refresh_token(
    refresh_token: Annotated[str, Body(..., embed=True)],
    user_manager: UserManagerDep,
    strategy: StrategyDep,
) -> BearerResponseExtended:
    token = await auth_backend.refresh(
        strategy=strategy,
        user_manager=user_manager,
        refresh_token=refresh_token,
    )
    if token is None:
        raise responses.INVALID_TOKEN.exception()
    return token
