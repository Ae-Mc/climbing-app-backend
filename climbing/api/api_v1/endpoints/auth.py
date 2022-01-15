from climbing.core.security import fastapi_users, auth_backend


router = fastapi_users.get_auth_router(backend=auth_backend)
