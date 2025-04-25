from fastapi import APIRouter

from .endpoints.files import router as files_router
from .endpoints.rating import router as rating_router

api_router = APIRouter()
api_router.include_router(rating_router, prefix="/rating", tags=["rating"])
