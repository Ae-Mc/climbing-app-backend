from fastapi import APIRouter

from climbing.core.security import auth_backend, fastapi_users

router = APIRouter()
router.include_router(fastapi_users.get_auth_router(backend=auth_backend))
router.include_router(fastapi_users.get_register_router())
router.include_router(fastapi_users.get_verify_router())
