"""Module for storing pydantic schemas"""

from .ascent import Ascent, AscentBase, AscentCreate, AscentUpdate
from .category import Category
from .competition import Competition
from .competition_participant import CompetitionParticipant
from .route import Route, RouteBase, RouteCreate, RouteUpdate
from .route_image import RouteImage
from .user import (
    AccessToken,
    User,
    UserBase,
    UserBaseWithCreatedAt,
    UserCreate,
    UserUpdate,
)

__all__ = [
    "AccessToken",
    "Ascent",
    "AscentBase",
    "AscentCreate",
    "AscentUpdate",
    "Category",
    "Competition",
    "CompetitionParticipant",
    "Route",
    "RouteBase",
    "RouteCreate",
    "RouteImage",
    "RouteUpdate",
    "User",
    "UserBase",
    "UserBaseWithCreatedAt",
    "UserCreate",
    "UserUpdate",
]
