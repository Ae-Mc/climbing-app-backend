from fastapi import APIRouter

from .endpoints import ascents, auth, competition, rating, routes, users

api_router = APIRouter()

api_router.include_router(ascents.router, prefix="/ascents", tags=["ascents"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(
    competition.router, prefix="/competitions", tags=["competitions"]
)
api_router.include_router(rating.router, prefix="/rating", tags=["rating"])
api_router.include_router(routes.router, prefix="/routes", tags=["routes"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
