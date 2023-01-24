from fastapi import APIRouter

from climbing.core.security import auth_backend, fastapi_users
from climbing.db.models import UserCreate
from climbing.schemas.base_read_classes import UserRead

router = APIRouter()
router.include_router(fastapi_users.get_auth_router(backend=auth_backend))
router.include_router(fastapi_users.get_register_router(UserRead, UserCreate))
router.include_router(fastapi_users.get_verify_router(UserRead))
