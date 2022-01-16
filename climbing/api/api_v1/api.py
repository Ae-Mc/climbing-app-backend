from fastapi import APIRouter

from .endpoints import auth, routes, users

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(routes.router, prefix="/routes", tags=["routes"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
