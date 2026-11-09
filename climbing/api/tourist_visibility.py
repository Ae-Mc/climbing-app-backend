"""Read-side visibility control. Never trust a client-provided tourist flag."""
from fastapi import Depends
from sqlalchemy import or_, select
from sqlmodel import col

from climbing.core.security import fastapi_users
from climbing.db.models.user import User
from climbing.db.models.route import Route
from climbing.db.models.ascent import Ascent

optional_user = fastapi_users.current_user(optional=True)

def may_view_tourists(viewer: User | None) -> bool:
    return bool(viewer and viewer.is_tourist)

def visible_route_clause(viewer: User | None):
    if may_view_tourists(viewer):
        return True
    return col(Route.author_id).in_(select(User.id).where(col(User.is_tourist).is_(False)))

def visible_ascent_clause(viewer: User | None):
    if may_view_tourists(viewer):
        return True
    return (
        col(Ascent.user_id).in_(select(User.id).where(col(User.is_tourist).is_(False)))
        & col(Ascent.route_id).in_(
            select(Route.id).where(visible_route_clause(viewer))
        )
    )
